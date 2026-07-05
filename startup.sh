#!/bin/bash
# No hacer cd: Oryx ya posiciona el cwd en el directorio de la app (/tmp/... o wwwroot).
set -e

if [ -f antenv/bin/activate ]; then
  source antenv/bin/activate
fi

exec gunicorn --bind=0.0.0.0:${PORT:-8000} --timeout 120 --workers 2 wsgi:app
