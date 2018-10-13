#! /usr/bin/env bash

echo "Port: $PORT"
python2 -V
python3 -V
python -V
exec python -m "$APP_MODULE"
