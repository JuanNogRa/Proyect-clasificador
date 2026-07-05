from __future__ import annotations

from typing import Union

from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from openai import AzureOpenAI, OpenAI

from src.config import AzureSettings, normalize_openai_endpoint

OpenAIClient = Union[OpenAI, AzureOpenAI]
FOUNDRY_TOKEN_SCOPE = "https://ai.azure.com/.default"
CLASSIC_TOKEN_SCOPE = "https://cognitiveservices.azure.com/.default"


def _is_foundry_v1_endpoint(endpoint: str) -> bool:
    return "/openai/v1" in endpoint.rstrip("/")


def get_openai_client(settings: AzureSettings) -> OpenAIClient:
    """Cliente OpenAI: Foundry v1 (portal) o Azure OpenAI clásico."""
    endpoint = normalize_openai_endpoint(settings.openai_endpoint)

    if _is_foundry_v1_endpoint(endpoint):
        if settings.openai_api_key:
            return OpenAI(base_url=endpoint, api_key=settings.openai_api_key)
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(),
            FOUNDRY_TOKEN_SCOPE,
        )
        return OpenAI(base_url=endpoint, api_key=token_provider)

    if settings.openai_api_key:
        return AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=settings.openai_api_key,
            api_version=settings.openai_api_version,
        )

    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(),
        CLASSIC_TOKEN_SCOPE,
    )
    return AzureOpenAI(
        azure_endpoint=endpoint,
        azure_ad_token_provider=token_provider,
        api_version=settings.openai_api_version,
    )


def get_search_credential(settings: AzureSettings) -> AzureKeyCredential:
    """Admin key de Search (requerida para indexar documentos)."""
    key = (settings.search_api_key or "").strip()
    if not key:
        raise ValueError(
            "Falta AZURE_SEARCH_API_KEY en .env. "
            "Obtén la Primary admin key en Portal > buscador-proyecto > Keys."
        )
    return AzureKeyCredential(key)


def get_search_index_client(settings: AzureSettings) -> SearchIndexClient:
    return SearchIndexClient(
        endpoint=settings.search_endpoint.rstrip("/"),
        credential=get_search_credential(settings),
    )


def get_search_client(settings: AzureSettings) -> SearchClient:
    return SearchClient(
        endpoint=settings.search_endpoint.rstrip("/"),
        index_name=settings.search_index_name,
        credential=get_search_credential(settings),
    )
