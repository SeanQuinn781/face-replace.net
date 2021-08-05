#!/bin/bash
# flask settings
export FLASK_APP=/var/www/html/face-replace/server/app/app.py
export FLASK_DEBUG=0

cd /var/www/html/face-replace/server/ && venv/bin/flask run

