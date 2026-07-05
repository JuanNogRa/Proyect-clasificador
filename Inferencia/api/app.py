from __future__ import annotations

import logging

import api.bootstrap  # noqa: F401 — carga Entrenamiento en sys.path

from flask import Flask, jsonify, request

from api.schemas import payload_to_series, prediction_to_dict
from src.config import AzureSettings
from src.rag_classifier import classify_case, classify_row

logger = logging.getLogger(__name__)


def create_app(settings: AzureSettings | None = None) -> Flask:
    app = Flask(__name__)
    app.config["SETTINGS"] = settings
    _settings_logged = False

    def get_settings() -> AzureSettings:
        nonlocal _settings_logged
        if app.config["SETTINGS"] is None:
            app.config["SETTINGS"] = AzureSettings.from_env()
        if not _settings_logged:
            s = app.config["SETTINGS"]
            logger.info(
                "Config Azure: openai=%s | search=%s | openai_key=%s | search_key=%s",
                s.openai_endpoint,
                s.search_endpoint,
                "configurada" if s.openai_api_key else "Managed Identity",
                "configurada" if s.search_api_key else "no configurada",
            )
            _settings_logged = True
        return app.config["SETTINGS"]

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "service": "rag-siniestros-inferencia"})

    @app.post("/v1/predict")
    def predict():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            logger.warning("POST /v1/predict: body JSON inválido")
            return jsonify({"error": "Body JSON inválido."}), 400

        top_k = data.get("top_k")
        query_text = data.get("query_text")
        numero_aviso = data.get("numero_aviso")
        logger.info(
            "POST /v1/predict: numero_aviso=%s top_k=%s query_text=%s",
            numero_aviso,
            top_k,
            "sí" if query_text else "no",
        )

        try:
            if query_text:
                result = classify_case(
                    str(query_text),
                    settings=get_settings(),
                    numero_aviso=str(numero_aviso or ""),
                    top_k=top_k,
                )
            else:
                row = payload_to_series(data)
                result = classify_row(row, settings=get_settings(), top_k=top_k)
        except ValueError as exc:
            logger.warning("Validación fallida (numero_aviso=%s): %s", numero_aviso, exc)
            return jsonify({"error": str(exc)}), 400
        except Exception as exc:
            logger.exception(
                "Error en inferencia (numero_aviso=%s): %s",
                numero_aviso,
                exc,
            )
            return jsonify({"error": f"Error en inferencia: {exc}"}), 500

        logger.info(
            "Inferencia OK (numero_aviso=%s): dictamen=%s",
            numero_aviso,
            result.dictamen,
        )
        return jsonify(prediction_to_dict(result))

    logger.info("App RAG siniestros inferencia lista")
    return app
