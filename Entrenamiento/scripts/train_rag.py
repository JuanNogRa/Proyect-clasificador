#!/usr/bin/env python
"""Indexa el corpus train en Azure AI Search (entrenamiento RAG)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd

from src.config import AzureSettings
from src.data_pipeline import agregar_por_aviso, split_avisos
from src.indexer import index_train_corpus


def main() -> None:
    parser = argparse.ArgumentParser(description="Entrenar corpus RAG en Azure AI Search")
    parser.add_argument(
        "--data",
        default=str(PROJECT_ROOT / "data" / "dataset_pt.csv"),
        help="Ruta al CSV original",
    )
    parser.add_argument(
        "--no-recreate-index",
        action="store_true",
        help="No eliminar/recrear el índice antes de indexar",
    )
    args = parser.parse_args()

    data_path = Path(args.data)
    raw = pd.read_csv(data_path, sep=";", low_memory=False)
    avisos = agregar_por_aviso(raw)
    train, val, test = split_avisos(avisos)

    settings = AzureSettings.from_env()
    indexed = index_train_corpus(
        train,
        settings,
        recreate_index=not args.no_recreate_index,
    )

    print(f"Indexados: {indexed} documentos de train")
    print(f"Val (no indexado): {len(val)} | Test (no indexado): {len(test)}")


if __name__ == "__main__":
    main()
