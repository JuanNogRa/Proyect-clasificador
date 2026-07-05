# Entrenamiento RAG — Siniestros vehiculares

Pipeline de indexación y evaluación del clasificador RAG con Azure OpenAI + Azure AI Search.

## Estructura

```
Entrenamiento/
├── data/                  # Dataset y predicciones exportadas
├── pt.ipynb               # Prueba técnica RAG + evaluación
├── pt - ml.ipynb          # Exploración ML (baseline)
├── scripts/
│   └── train_rag.py       # Indexa train en Azure AI Search
├── src/                   # Módulos del pipeline
│   ├── config.py
│   ├── azure_clients.py
│   ├── documents.py
│   ├── data_pipeline.py
│   ├── indexer.py
│   ├── rag_classifier.py
│   └── evaluate.py
├── .env.example
└── requirements.txt
```

## Configuración (conda — entorno `base`)

Usa el mismo entorno conda que el notebook `pt.ipynb` (`display_name: base`).

**Anaconda Prompt** o terminal con conda inicializado:

```bash
conda activate base
pip install -r requirements.txt
copy .env.example .env   # completar credenciales Azure
```

Si faltan paquetes, con el entorno `base` activo:

```bash
pip install -r requirements.txt
pip install -r ../Inferencia/requirements.txt
```

O crea un entorno dedicado:

```bash
conda env create -f ../environment.yml
conda activate subocol-rag
```

## Indexar corpus (train)

```bash
conda activate base
python scripts/train_rag.py
```

## Notebook

Abrir `pt.ipynb` con el directorio de trabajo en `Entrenamiento/` (para que `./data/` y `from src...` resuelvan bien).
