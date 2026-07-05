"""Punto de entrada Flask: `flask --app app run` desde Inferencia/."""

import os
import sys
from pathlib import Path

INFERENCIA_ROOT = Path(__file__).resolve().parent
if str(INFERENCIA_ROOT) not in sys.path:
    sys.path.insert(0, str(INFERENCIA_ROOT))

from api.app import create_app

app = create_app()

if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "8000"))
    debug = os.getenv("FLASK_DEBUG", "false").lower() in {"1", "true", "yes"}
    app.run(host=host, port=port, debug=debug)
