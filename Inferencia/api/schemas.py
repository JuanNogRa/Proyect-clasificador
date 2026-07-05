from __future__ import annotations

import pandas as pd

REQUIRED_FIELDS = (
    "numero_aviso",
    "version_hechos",
    "piezas_totales",
    "piezas_cambio",
)


def _missing_fields(data: dict, fields: tuple[str, ...]) -> list[str]:
    return [field for field in fields if field not in data or data[field] in (None, "")]


def payload_to_series(data: dict) -> pd.Series:
    """Convierte JSON de inferencia al formato esperado por build_case_text."""
    missing = _missing_fields(data, REQUIRED_FIELDS)
    if missing:
        raise ValueError(f"Campos obligatorios faltantes: {', '.join(missing)}")

    vehiculo = data.get("vehiculo")
    if not vehiculo:
        vehiculo_parts = [
            data.get("tipo_carroceria"),
            data.get("marca"),
            data.get("linea"),
            data.get("modelo"),
        ]
        vehiculo = " ".join(str(part) for part in vehiculo_parts if part)
    if not vehiculo:
        raise ValueError(
            "Indica 'vehiculo' o la combinación tipo_carroceria/marca/linea/modelo."
        )

    piezas_texto = data.get("piezas_texto")
    if not piezas_texto:
        piezas = data.get("piezas")
        if piezas:
            piezas_texto = ", ".join(str(p) for p in piezas)
    if not piezas_texto:
        raise ValueError("Indica 'piezas_texto' o una lista 'piezas'.")

    return pd.Series(
        {
            "numero_aviso": str(data["numero_aviso"]),
            "vehiculo": str(vehiculo),
            "version_hechos": str(data["version_hechos"]),
            "piezas_texto": str(piezas_texto),
            "piezas_totales": data["piezas_totales"],
            "piezas_cambio": data["piezas_cambio"],
        }
    )


def prediction_to_dict(result) -> dict:
    return {
        "numero_aviso": result.numero_aviso,
        "dictamen": result.dictamen,
        "confianza": result.confianza,
        "razones": result.razones,
        "casos_similares": result.casos_similares,
    }
