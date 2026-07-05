from __future__ import annotations

import pandas as pd


def build_case_text(row: pd.Series, *, include_dictamen: bool = False) -> str:
    """Texto unificado para indexación, búsqueda híbrida y prompts."""
    parts = [
        f"AVISO: {row['numero_aviso']}",
        f"VEHICULO: {row['vehiculo']}",
        f"VERSION DE HECHOS: {row['version_hechos']}",
        f"PIEZAS AFECTADAS: {row['piezas_texto']}",
        f"PIEZAS TOTALES: {row['piezas_totales']}",
        f"PIEZAS CAMBIO: {row['piezas_cambio']}",
    ]
    if include_dictamen:
        parts.append(f"DICTAMEN: {row['estado_aviso']}")
    return "\n".join(parts)


def row_to_search_document(row: pd.Series) -> dict:
    """Documento para Azure AI Search (solo train)."""
    return {
        "id": str(row["numero_aviso"]),
        "numero_aviso": str(row["numero_aviso"]),
        "content": build_case_text(row, include_dictamen=True),
        "version_hechos": str(row["version_hechos"]),
        "piezas_texto": str(row["piezas_texto"]),
        "vehiculo": str(row["vehiculo"]),
        "estado_aviso": str(row["estado_aviso"]),
    }


def row_to_query(row: pd.Series) -> dict:
    """Consulta para inferencia (sin dictamen)."""
    return {
        "numero_aviso": str(row["numero_aviso"]),
        "query_text": build_case_text(row, include_dictamen=False),
        "estado_aviso_real": str(row["estado_aviso"]),
    }
