from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def _require(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(
            f"Falta la variable de entorno '{name}'. "
            f"Copia .env.example a .env y completa los valores."
        )
    return value


def normalize_openai_endpoint(endpoint: str) -> str:
    """Normaliza URLs de Azure AI Foundry al endpoint OpenAI v1 del portal."""
    endpoint = endpoint.strip().rstrip("/")
    if endpoint and "://" not in endpoint:
        endpoint = f"https://{endpoint}"

    if "/openai/v1" in endpoint:
        return endpoint.split("/openai/v1", 1)[0] + "/openai/v1"

    if "/api/projects/" in endpoint:
        endpoint = endpoint.split("/api/projects/")[0]

    if "services.ai.azure.com" in endpoint:
        resource = endpoint.split("://", 1)[1].split(".", 1)[0]
        return f"https://{resource}.services.ai.azure.com/openai/v1"

    if "openai.azure.com" in endpoint:
        resource = endpoint.split("://", 1)[1].split(".", 1)[0]
        return f"https://{resource}.services.ai.azure.com/openai/v1"

    return f"{endpoint}/"


@dataclass(frozen=True)
class AzureSettings:
    openai_endpoint: str
    openai_api_version: str
    chat_deployment: str
    embedding_deployment: str
    embedding_dimensions: int
    search_endpoint: str
    search_index_name: str
    openai_api_key: str | None
    search_api_key: str | None
    rag_top_k: int

    @classmethod
    def from_env(cls) -> "AzureSettings":
        return cls(
            openai_endpoint=normalize_openai_endpoint(_require("AZURE_OPENAI_ENDPOINT")),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview"),
            chat_deployment=_require("AZURE_OPENAI_CHAT_DEPLOYMENT"),
            embedding_deployment=_require("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
            embedding_dimensions=int(os.getenv("AZURE_OPENAI_EMBEDDING_DIMENSIONS", "1536")),
            search_endpoint=_require("AZURE_SEARCH_ENDPOINT"),
            search_index_name=os.getenv("AZURE_SEARCH_INDEX_NAME", "siniestros-rag"),
            openai_api_key=os.getenv("AZURE_OPENAI_API_KEY") or None,
            search_api_key=(os.getenv("AZURE_SEARCH_API_KEY") or "").strip() or None,
            rag_top_k=int(os.getenv("RAG_TOP_K", "5")),
        )
