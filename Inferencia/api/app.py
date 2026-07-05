from __future__ import annotations

import api.bootstrap  # noqa: F401 — carga Entrenamiento en sys.path

from flask import Flask, jsonify, request

from api.schemas import payload_to_series, prediction_to_dict
from src.config import AzureSettings
from src.documents import build_case_text
from src.rag_classifier import classify_case, classify_row


def create_app(settings: AzureSettings | None = None) -> Flask:
    app = Flask(__name__)
    app.config["SETTINGS"] = settings

    def get_settings() -> AzureSettings:
        if app.config["SETTINGS"] is None:
            app.config["SETTINGS"] = AzureSettings.from_env()
        return app.config["SETTINGS"]

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "service": "rag-siniestros-inferencia"})

    @app.post("/v1/predict")
    def predict():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"error": "Body JSON inválido."}), 400

        top_k = data.get("top_k")
        query_text = data.get("query_text")

        try:
            if query_text:
                result = classify_case(
                    str(query_text),
                    settings=get_settings(),
                    numero_aviso=str(data.get("numero_aviso", "")),
                    top_k=top_k,
                )
            else:
                row = payload_to_series(data)
                result = classify_row(row, settings=get_settings(), top_k=top_k)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception as exc:
            return jsonify({"error": f"Error en inferencia: {exc}"}), 500

        return jsonify(prediction_to_dict(result))

    return app
