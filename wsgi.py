"""Punto de entrada WSGI para Azure App Service (raíz del repo)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INFERENCIA = ROOT / "Inferencia"
if str(INFERENCIA) not in sys.path:
    sys.path.insert(0, str(INFERENCIA))

from app import app  # noqa: E402  → Inferencia/app.py
