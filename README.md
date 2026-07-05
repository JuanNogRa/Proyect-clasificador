# Proyecto Subocol IA — RAG siniestros

| Carpeta | Contenido |
|---------|-----------|
| **Entrenamiento/** | Pipeline RAG, notebooks, indexación y evaluación |
| **Inferencia/** | API Flask para clasificar avisos en producción |

- Entrenamiento: [Entrenamiento/README.md](Entrenamiento/README.md)
- Inferencia: [Inferencia/README.md](Inferencia/README.md)
- **Deploy Azure (GitHub Actions):** [docs/DEPLOY-AZURE.md](docs/DEPLOY-AZURE.md)

## Entorno conda

Entrenamiento e inferencia usan el mismo entorno conda **`base`** (como `pt.ipynb`).

```bash
conda activate base
pip install -r Entrenamiento/requirements.txt
pip install -r Inferencia/requirements.txt
```
