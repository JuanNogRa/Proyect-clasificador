#!/bin/bash
# Arranque alternativo si el Startup Command apunta aquí.
cd /home/site/wwwroot
exec gunicorn --bind=0.0.0.0:${PORT:-8000} --timeout 120 --workers 2 wsgi:app
