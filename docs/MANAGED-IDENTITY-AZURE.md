# Managed Identity — Web App sin API keys

Autenticación entre **rag-siniestros-api** (App Service) y **Azure OpenAI** + **Azure AI Search** usando identidad administrada, sin `AZURE_OPENAI_API_KEY` ni `AZURE_SEARCH_API_KEY`.

---

## Parte 1 — Activar identidad en la Web App

1. Portal Azure → **rag-siniestros-api**
2. **Settings** → **Identity** (Identidad)
3. Pestaña **System assigned** (Asignada por el sistema)
4. **Status** → **On** → **Save** → **Yes**
5. Copia el **Object (principal) ID** — lo usarás para verificar roles

---

## Parte 2 — Rol en Azure OpenAI / Foundry

1. Portal → tu recurso **Azure OpenAI** o **Azure AI Foundry** (el del endpoint)
2. **Access control (IAM)** → **Add** → **Add role assignment**
3. **Role** → busca y selecciona:
   - **`Cognitive Services OpenAI User`** (recomendado), o
   - **`Cognitive Services User`**
4. **Next** → **Members** → **Managed identity**
5. **Select members** → **App Service** → elige **rag-siniestros-api**
6. **Review + assign**

---

## Parte 3 — Rol en Azure AI Search

1. Portal → tu recurso **Azure AI Search**
2. **Access control (IAM)** → **Add role assignment**
3. **Role** → **`Search Index Data Reader`** (solo inferencia / consultas)
4. **Members** → **Managed identity** → **App Service** → **rag-siniestros-api**
5. **Review + assign**

> Para **indexar** desde tu PC o un pipeline de train sin key, necesitarías además **`Search Index Data Contributor`** en Search.

---

## Parte 4 — Variables en App Service (sin keys)

**Environment variables** → quita o deja **vacías**:
- `AZURE_OPENAI_API_KEY`
- `AZURE_SEARCH_API_KEY`

Mantén estas (sin secrets):

```json
[
  { "name": "AZURE_OPENAI_ENDPOINT", "value": "https://TU-RECURSO.services.ai.azure.com/openai/v1", "slotSetting": false },
  { "name": "AZURE_OPENAI_API_VERSION", "value": "2024-08-01-preview", "slotSetting": false },
  { "name": "AZURE_OPENAI_CHAT_DEPLOYMENT", "value": "gpt-5-mini", "slotSetting": false },
  { "name": "AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "value": "text-embedding-3-small", "slotSetting": false },
  { "name": "AZURE_OPENAI_EMBEDDING_DIMENSIONS", "value": "1536", "slotSetting": false },
  { "name": "AZURE_SEARCH_ENDPOINT", "value": "https://TU-RECURSO.search.windows.net", "slotSetting": false },
  { "name": "AZURE_SEARCH_INDEX_NAME", "value": "siniestros-rag", "slotSetting": false },
  { "name": "RAG_TOP_K", "value": "8", "slotSetting": false },
  { "name": "WEBSITES_PORT", "value": "8000", "slotSetting": false }
]
```

**Apply** → reinicia la app (1–2 min).

---

## Parte 5 — Red (igual que con keys)

En **OpenAI** y **Search** → **Networking**:
- Acceso **All networks** / **Public access: Yes**

Managed Identity no sustituye la red; si el servicio está privado, la Web App no conectará.

---

## Parte 6 — Desplegar código actualizado

El repo ya soporta Search sin API key (usa `DefaultAzureCredential`).

```powershell
git add Entrenamiento/src/azure_clients.py
git commit -m "Soporte Managed Identity para Azure Search"
git push origin main
```

Espera deploy verde → prueba POST `/v1/predict`.

---

## Resumen de roles

| Recurso | Rol | Para qué |
|---------|-----|----------|
| Azure OpenAI | `Cognitive Services OpenAI User` | Chat + embeddings |
| Azure AI Search | `Search Index Data Reader` | Consultas RAG (inferencia) |
| Azure AI Search | `Search Index Data Contributor` | Solo si indexas sin key |

---

## Local vs Azure

| Entorno | Sin keys |
|---------|----------|
| **App Service** | Managed Identity (pasos arriba) |
| **Tu PC** | `az login` + keys vacías en `.env`, o sigue usando keys en `.env` |

---

## Errores comunes

| Error | Causa |
|-------|--------|
| `DefaultAzureCredential failed` | Identity Off o roles no asignados (espera 5–10 min) |
| `403 Forbidden` | Falta rol en OpenAI o Search |
| `Connection error` | Networking privado en OpenAI/Search |
