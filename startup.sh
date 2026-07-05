#!/bin/bash
cd /home/site/wwwroot
python -m gunicorn --bind=0.0.0.0:${PORT:-8000} --timeout 120 --workers 2 wsgi:app
