#!/bin/bash
# Comando de arranque en Azure App Service (Linux).
cd /home/site/wwwroot/Inferencia
exec gunicorn --bind=0.0.0.0:${PORT:-8000} --timeout 120 --workers 2 app:app
