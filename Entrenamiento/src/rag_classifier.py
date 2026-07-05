from __future__ import annotations

import json
import re
from dataclasses import dataclass

from azure.search.documents.models import VectorizedQuery
from openai import AzureOpenAI

from src.azure_clients import get_openai_client, get_search_client
from src.config import AzureSettings
from src.documents import build_case_text
from src.indexer import embed_texts

SYSTEM_PROMPT = """Eres un analista senior de seguros vehiculares.
Clasifica si un siniestro queda ENTREGADO u OBJETADO.

Criterio principal: coherencia entre versión de hechos y piezas afectadas,
PERO la coherencia física NO es suficiente para ENTREGADO.

Clasifica OBJETADO si ocurre AL MENOS UNA de estas condiciones:
1. Inconsistencia entre relato y piezas (lado, tipo de impacto, piezas no explicadas).
2. Mención de tercero responsable, reversa de tercero, o responsabilidad del otro conductor
   sin evidencia clara de cobertura procedente en este aviso.
3. Datos incompletos o sospechosos (vehículo no identificado, relato vago).
4. Entre los casos históricos similares recuperados, hay AL MENOS UNO con dictamen OBJETADO
   y el caso nuevo comparte el mismo patón (colisión en parqueadero, reversa, tercero, etc.).
5. Ante cualquier duda razonable → OBJETADO.

Clasifica ENTREGADO SOLO si:
- Relato y piezas son claramente coherentes, Y
- La mayoría de casos históricos similares son ENTREGADO, Y
- No hay señales de exclusión ni tercero responsable que impida el pago.

Criterio de negocio (obligatorio):
- Prioriza recall de OBJETADO: preferir auditoría manual antes que pagar indebidamente.
- Si confianza < 0.9 y hay cualquier señal de OBJETADO → clasifica OBJETADO.

Usa los casos históricos como referencia de PATRÓN y DICTAMEN, no solo de coherencia física.

Responde SOLO con JSON válido:
{
  "dictamen": "ENTREGADO" | "OBJETADO",
  "confianza": 0.0-1.0,
  "razones": ["...", "..."]
}
"""


@dataclass
class PredictionResult:
    numero_aviso: str
    dictamen: str
    confianza: float
    razones: list[str]
    casos_similares: list[str]
    estado_aviso_real: str | None = None


def _parse_json_response(content: str) -> dict:
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
    return json.loads(content)


def retrieve_similar_cases(
    query_text: str,
    settings: AzureSettings,
    *,
    top_k: int | None = None,
) -> list[dict]:
    top_k = top_k or settings.rag_top_k
    openai_client = get_openai_client(settings)
    search_client = get_search_client(settings)

    query_vector = embed_texts(openai_client, settings, [query_text])[0]
    vector_query = VectorizedQuery(
        vector=query_vector,
        k_nearest_neighbors=top_k,
        fields="content_vector",
    )

    results = search_client.search(
        search_text=query_text,
        vector_queries=[vector_query],
        select=["numero_aviso", "content", "estado_aviso", "vehiculo"],
        top=top_k,
    )

    return [dict(item) for item in results]


def _build_user_prompt(query_text: str, similar_cases: list[dict]) -> str:
    examples = []
    for idx, case in enumerate(similar_cases, start=1):
        examples.append(
            f"### Caso histórico {idx}\n"
            f"Numero aviso: {case.get('numero_aviso')}\n"
            f"Dictamen histórico: {case.get('estado_aviso')}\n"
            f"{case.get('content', '')}"
        )

    examples_text = "\n\n".join(examples) if examples else "Sin casos similares recuperados."
    return (
        "Casos históricos similares:\n"
        f"{examples_text}\n\n"
        "Caso nuevo a clasificar:\n"
        f"{query_text}"
    )


def classify_case(
    query_text: str,
    settings: AzureSettings | None = None,
    *,
    numero_aviso: str | None = None,
    estado_aviso_real: str | None = None,
    top_k: int | None = None,
) -> PredictionResult:
    settings = settings or AzureSettings.from_env()
    openai_client = get_openai_client(settings)

    similar_cases = retrieve_similar_cases(query_text, settings, top_k=top_k)
    user_prompt = _build_user_prompt(query_text, similar_cases)

    response = openai_client.chat.completions.create(
        model=settings.chat_deployment,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    parsed = _parse_json_response(response.choices[0].message.content or "{}")
    dictamen = str(parsed.get("dictamen", "OBJETADO")).upper()
    if dictamen not in {"ENTREGADO", "OBJETADO"}:
        dictamen = "OBJETADO"

    return PredictionResult(
        numero_aviso=numero_aviso or "",
        dictamen=dictamen,
        confianza=float(parsed.get("confianza", 0.5)),
        razones=list(parsed.get("razones", [])),
        casos_similares=[str(c.get("numero_aviso", "")) for c in similar_cases],
        estado_aviso_real=estado_aviso_real,
    )


def classify_row(row, settings: AzureSettings | None = None, **kwargs) -> PredictionResult:
    query_text = build_case_text(row, include_dictamen=False)
    estado = row.get("estado_aviso")
    return classify_case(
        query_text,
        settings=settings,
        numero_aviso=str(row["numero_aviso"]),
        estado_aviso_real=str(estado) if estado is not None else None,
        **kwargs,
    )
