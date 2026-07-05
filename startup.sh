#!/bin/bash
set -e
cd /home/site/wwwroot

# Oryx instala dependencias en antenv durante el deploy
if [ -f antenv/bin/activate ]; then
  source antenv/bin/activate
fi

exec gunicorn --bind=0.0.0.0:${PORT:-8000} --timeout 120 --workers 2 wsgi:app
