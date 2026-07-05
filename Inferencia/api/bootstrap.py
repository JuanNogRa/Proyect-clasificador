"""Conecta Inferencia con los módulos RAG de Entrenamiento."""

from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

from api.logging_config import configure_logging

configure_logging()

INFERENCIA_ROOT = Path(__file__).resolve().parent.parent
ENTRENAMIENTO_ROOT = INFERENCIA_ROOT.parent / "Entrenamiento"

if not ENTRENAMIENTO_ROOT.is_dir():
    raise RuntimeError(
        f"No se encontró la carpeta Entrenamiento en {ENTRENAMIENTO_ROOT.parent}"
    )

load_dotenv(INFERENCIA_ROOT / ".env")
load_dotenv(ENTRENAMIENTO_ROOT / ".env")

if str(ENTRENAMIENTO_ROOT) not in sys.path:
    sys.path.insert(0, str(ENTRENAMIENTO_ROOT))
