#! /usr/bin/env bash

python2 -m virtualenv py2venv
py2venv/bin/pip install ansible-review

echo "Port: $PORT"
exec python -m "$APP_MODULE"
