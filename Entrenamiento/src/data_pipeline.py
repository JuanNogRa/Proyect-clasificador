from __future__ import annotations

import pandas as pd
from sklearn.model_selection import train_test_split


def agregar_por_aviso(df: pd.DataFrame) -> pd.DataFrame:
    """Consolida el dataset de piezas en un registro por siniestro."""
    return (
        df.groupby("numero_aviso", as_index=False)
        .agg(
            fecha_creacion=("fecha_creacion", "first"),
            tipo_carroceria=("tipo_carroceria", "first"),
            marca=("marca", "first"),
            linea=("linea", "first"),
            version=("version", "first"),
            modelo=("modelo", "first"),
            version_hechos=("version_hechos", "first"),
            piezas_totales=("piezas_totales", "first"),
            piezas_cambio=("piezas_cambio", "first"),
            piezas=("nombre_irs", lambda x: sorted(set(x.dropna().astype(str)))),
            codigos_irs=("codigo_irs", lambda x: sorted(set(x.dropna().astype(str)))),
            num_piezas_registradas=("nombre_irs", "nunique"),
            estado_aviso=("estado_aviso", "first"),
        )
        .assign(
            piezas_texto=lambda d: d["piezas"].apply(lambda p: ", ".join(p)),
            vehiculo=lambda d: (
                d["tipo_carroceria"].astype(str)
                + " "
                + d["marca"].astype(str)
                + " "
                + d["linea"].astype(str)
                + " "
                + d["modelo"].astype(str)
            ),
        )
    )


def split_avisos(
    avisos: pd.DataFrame,
    *,
    random_state: int = 42,
    test_size: float = 0.15,
    val_size: float = 0.15,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train_val, test = train_test_split(
        avisos,
        test_size=test_size,
        stratify=avisos["estado_aviso"],
        random_state=random_state,
    )
    val_ratio = val_size / (1 - test_size)
    train, val = train_test_split(
        train_val,
        test_size=val_ratio,
        stratify=train_val["estado_aviso"],
        random_state=random_state,
    )
    return train.reset_index(drop=True), val.reset_index(drop=True), test.reset_index(drop=True)
