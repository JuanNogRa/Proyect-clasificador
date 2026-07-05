from __future__ import annotations

import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix

from src.config import AzureSettings
from src.rag_classifier import classify_row


def evaluate_dataframe(
    df: pd.DataFrame,
    settings: AzureSettings | None = None,
    *,
    max_samples: int | None = None,
    top_k: int | None = None,
) -> tuple[pd.DataFrame, dict]:
    subset = df.head(max_samples) if max_samples else df
    predictions = []

    for _, row in subset.iterrows():
        result = classify_row(row, settings=settings, top_k=top_k)
        predictions.append(
            {
                "numero_aviso": result.numero_aviso,
                "dictamen_real": result.estado_aviso_real,
                "dictamen_pred": result.dictamen,
                "confianza": result.confianza,
                "razones": " | ".join(result.razones),
                "casos_similares": ", ".join(result.casos_similares),
            }
        )

    results_df = pd.DataFrame(predictions)
    y_true = results_df["dictamen_real"]
    y_pred = results_df["dictamen_pred"]

    report = classification_report(
        y_true,
        y_pred,
        labels=["ENTREGADO", "OBJETADO"],
        output_dict=True,
        zero_division=0,
    )
    metrics = {
        "classification_report": report,
        "confusion_matrix": confusion_matrix(
            y_true, y_pred, labels=["ENTREGADO", "OBJETADO"]
        ).tolist(),
        "n_samples": len(results_df),
    }
    return results_df, metrics
