# Inferencia — API Flask RAG

Servicio HTTP para clasificar siniestros con el modelo RAG indexado en Azure.

Reutiliza los módulos de `../Entrenamiento/src` (sin duplicar código).

## Requisitos previos

1. Índice train ya creado en Azure AI Search (`Entrenamiento/scripts/train_rag.py`).
2. Variables Azure en `Entrenamiento/.env` (Inferencia las carga como fallback).
3. Entorno conda **`base`** — el mismo del notebook de entrenamiento.

## Instalación (Miniconda)

Tu Miniconda está en: `C:\Users\Juan Noguera\Documents\Miniconda`

**No necesitas `conda activate`** si usas los scripts del proyecto (detectan Miniconda solos).

Primera vez — instalar dependencias:

```bash
cd Inferencia
scripts\install_deps.bat
```

## Levantar API

```bash
cd Inferencia
scripts\run_api.bat
```

En PowerShell:

```powershell
cd Inferencia
.\scripts\run_api.ps1
```

La API queda en **http://localhost:8000**

### (Opcional) Agregar conda al PATH

Para poder usar `conda activate base` en cualquier terminal:

```powershell
& "$env:USERPROFILE\Documents\Miniconda\Scripts\conda.exe" init powershell
```

Cierra y abre la terminal. Luego:

```bash
conda activate base
cd Inferencia
python scripts/run_api.py
```

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/v1/predict` | Clasificar un aviso |
| POST | `/v1/predict/batch` | Clasificar varios avisos |
| POST | `/v1/predict/preview-text` | Ver texto enviado a Search/LLM |

## Ejemplo

```bash
curl -X POST http://localhost:8000/v1/predict ^
  -H "Content-Type: application/json" ^
  -d "{\"numero_aviso\":\"231121\",\"vehiculo\":\"sedan TOYOTA COROLLA 2020\",\"version_hechos\":\"colision lateral\",\"piezas_texto\":\"puerta del, guardafango del\",\"piezas_totales\":5,\"piezas_cambio\":3}"
```

Respuesta:

```json
{
  "numero_aviso": "231121",
  "dictamen": "OBJETADO",
  "confianza": 0.92,
  "razones": ["..."],
  "casos_similares": ["175898", "205847"]
}
```

## Notas

- Si `conda` no se reconoce en PowerShell normal, ejecuta `conda init powershell` y reinicia la terminal, o usa **Anaconda Prompt**.
- Las credenciales Azure se leen de `Inferencia/.env` y, si no existen, de `Entrenamiento/.env`.
