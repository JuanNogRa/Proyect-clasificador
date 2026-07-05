#!/usr/bin/env python
"""Levanta la API Flask de inferencia RAG."""

from __future__ import annotations

import os
import sys
from pathlib import Path

INFERENCIA_ROOT = Path(__file__).resolve().parent.parent
if str(INFERENCIA_ROOT) not in sys.path:
    sys.path.insert(0, str(INFERENCIA_ROOT))

from api.app import create_app

if __name__ == "__main__":
    app = create_app()
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "8000"))
    debug = os.getenv("FLASK_DEBUG", "false").lower() in {"1", "true", "yes"}
    print(f"API inferencia en http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)
