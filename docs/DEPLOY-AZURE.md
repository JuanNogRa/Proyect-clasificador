# Despliegue automático: GitHub Actions → Azure App Service

Guía paso a paso para publicar la API de **Inferencia** en Azure cada vez que hagas `push` a `main`.

## Arquitectura

```
GitHub (push main) → GitHub Actions → Azure App Service (Linux + Python)
                                              ↓
                                    Azure OpenAI + AI Search
```

El índice RAG debe existir **antes** (correr `Entrenamiento/scripts/train_rag.py` una vez).

---

## Parte 1 — Crear App Service en Azure (una sola vez)

### 1.1 Crear la Web App

1. [Portal Azure](https://portal.azure.com) → **Create a resource** → **Web App**
2. Configuración recomendada:
   - **Publish:** Code
   - **Runtime stack:** Python 3.11
   - **Operating System:** Linux
   - **Region:** misma que OpenAI y AI Search
   - **Pricing:** B1 (pruebas) o S1 (producción)
3. Anota el nombre, ej. `rag-siniestros-api` → URL: `https://rag-siniestros-api.azurewebsites.net`

### 1.2 Comando de arranque

En la Web App → **Configuration** → **General settings**:

| Campo | Valor |
|-------|--------|
| **Startup Command** | `bash startup.sh` |
| **Always On** | On (recomendado) |

Guarda y reinicia si pide.

### 1.3 Variables de entorno

**Configuration** → **Application settings** → **New application setting**:

| Nombre | Valor |
|--------|--------|
| `WEBSITES_PORT` | `8000` |
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | `true` |
| `AZURE_OPENAI_ENDPOINT` | tu endpoint OpenAI v1 |
| `AZURE_OPENAI_API_VERSION` | `2024-08-01-preview` |
| `AZURE_OPENAI_CHAT_DEPLOYMENT` | ej. `gpt-5-mini` |
| `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` | ej. `text-embedding-3-small` |
| `AZURE_OPENAI_EMBEDDING_DIMENSIONS` | `1536` |
| `AZURE_OPENAI_API_KEY` | tu key (o Managed Identity) |
| `AZURE_SEARCH_ENDPOINT` | tu Search endpoint |
| `AZURE_SEARCH_INDEX_NAME` | `siniestros-rag` |
| `AZURE_SEARCH_API_KEY` | tu key Search |
| `RAG_TOP_K` | `8` |

No subas `.env` al repositorio; solo configúralo aquí.

### 1.4 Descargar Publish Profile

En la Web App → **Overview** → **Download publish profile** (archivo `.PublishSettings`).

---

## Parte 2 — Subir código a GitHub

```bash
cd Proyecto
git init
git add .
git commit -m "Proyecto RAG: entrenamiento + inferencia"
git branch -M main
git remote add origin https://github.com/TU-USUARIO/TU-REPO.git
git push -u origin main
```

Asegúrate de que **no** se suban `.env` (están en `.gitignore`).

---

## Parte 3 — Secrets en GitHub (una sola vez)

En GitHub → tu repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**:

| Secret | Valor |
|--------|--------|
| `AZURE_WEBAPP_NAME` | Nombre de la Web App, ej. `rag-siniestros-api` |
| `AZURE_WEBAPP_PUBLISH_PROFILE` | Contenido **completo** del archivo `.PublishSettings` (XML) |

---

## Parte 4 — Despliegue automático

El workflow está en `.github/workflows/deploy-inferencia.yml`.

Se ejecuta cuando:
- Haces **push a `main`** y cambian archivos en `Inferencia/`, `Entrenamiento/src/` o el workflow
- O manualmente: **Actions** → **Deploy API Inferencia** → **Run workflow**

### Ver el progreso

GitHub → **Actions** → clic en el run → revisa logs de **Deploy to Azure Web App**.

### Probar en producción

```bash
curl https://rag-siniestros-api.azurewebsites.net/health
```

```bash
curl -X POST https://rag-siniestros-api.azurewebsites.net/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"numero_aviso":"281375","vehiculo":"camioneta JEEP COMPASS SPORT 2019","version_hechos":"...","piezas_texto":"broche carroceria, farol tapabarros derecho","piezas_totales":2,"piezas_cambio":2}'
```

---

## Estructura que se despliega

Azure recibe el repo completo; la API necesita:

```
wwwroot/
├── Inferencia/          ← Flask + gunicorn (startup.sh)
├── Entrenamiento/src/   ← módulos RAG (importados por bootstrap)
└── requirements.txt     ← Oryx instala dependencias al deploy
```

---

## Solución de problemas

| Síntoma | Qué revisar |
|---------|-------------|
| 502 / app no arranca | **Log stream** en App Service; startup command `bash Inferencia/startup.sh` |
| ModuleNotFoundError | `requirements.txt` en raíz; `SCM_DO_BUILD_DURING_DEPLOYMENT=true` |
| Error Azure OpenAI/Search | Application settings; keys y endpoints |
| Deploy falla en GitHub | Secret `AZURE_WEBAPP_PUBLISH_PROFILE` completo; nombre correcto en `AZURE_WEBAPP_NAME` |
| Timeout en predict | Subir timeout en `startup.sh` (`--timeout 180`) |

**Ver logs en vivo:** App Service → **Monitoring** → **Log stream**

---

## Opcional: deploy manual sin GitHub

```bash
az login
az webapp up --name rag-siniestros-api --resource-group TU-RG --runtime "PYTHON:3.11"
```

Para producción, GitHub Actions es preferible (historial, rollback, CI).
