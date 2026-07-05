from __future__ import annotations

import pandas as pd
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    VectorSearch,
    VectorSearchProfile,
)

from src.azure_clients import OpenAIClient, get_openai_client, get_search_client, get_search_index_client
from src.config import AzureSettings
from src.documents import row_to_search_document


def _build_index_schema(settings: AzureSettings) -> SearchIndex:
    fields = [
        SearchField(name="id", type=SearchFieldDataType.String, key=True, filterable=True),
        SearchField(name="numero_aviso", type=SearchFieldDataType.String, filterable=True),
        SearchField(name="content", type=SearchFieldDataType.String, searchable=True),
        SearchField(name="version_hechos", type=SearchFieldDataType.String, searchable=True),
        SearchField(name="piezas_texto", type=SearchFieldDataType.String, searchable=True),
        SearchField(name="vehiculo", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SearchField(name="estado_aviso", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=settings.embedding_dimensions,
            vector_search_profile_name="vector-profile",
        ),
    ]

    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name="hnsw")],
        profiles=[
            VectorSearchProfile(
                name="vector-profile",
                algorithm_configuration_name="hnsw",
            )
        ],
    )

    return SearchIndex(
        name=settings.search_index_name,
        fields=fields,
        vector_search=vector_search,
    )


def create_or_replace_index(settings: AzureSettings) -> None:
    index_client = get_search_index_client(settings)
    try:
        index_client.delete_index(settings.search_index_name)
    except ResourceNotFoundError:
        pass
    index_client.create_index(_build_index_schema(settings))


def embed_texts(client: OpenAIClient, settings: AzureSettings, texts: list[str]) -> list[list[float]]:
    response = client.embeddings.create(
        model=settings.embedding_deployment,
        input=texts,
    )
    return [item.embedding for item in response.data]


def index_train_corpus(
    train: pd.DataFrame,
    settings: AzureSettings | None = None,
    *,
    batch_size: int = 16,
    recreate_index: bool = True,
) -> int:
    """Entrenamiento RAG: crea el índice e indexa solo el conjunto train."""
    settings = settings or AzureSettings.from_env()
    openai_client = get_openai_client(settings)

    if recreate_index:
        create_or_replace_index(settings)

    search_client = get_search_client(settings)
    documents = [row_to_search_document(row) for _, row in train.iterrows()]

    indexed = 0
    for start in range(0, len(documents), batch_size):
        batch = documents[start : start + batch_size]
        vectors = embed_texts(openai_client, settings, [doc["content"] for doc in batch])
        for doc, vector in zip(batch, vectors):
            doc["content_vector"] = vector
        try:
            result = search_client.upload_documents(documents=batch)
        except HttpResponseError as exc:
            if exc.status_code == 403:
                raise PermissionError(
                    "Azure AI Search rechazó la carga de documentos (403 Forbidden). "
                    "Verifica AZURE_SEARCH_API_KEY en .env (Primary admin key del servicio Search)."
                ) from exc
            raise
        indexed += sum(1 for item in result if item.succeeded)

    return indexed
