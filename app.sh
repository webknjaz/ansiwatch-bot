#! /usr/bin/env bash

curl https://bootstrap.pypa.io/get-pip.py | python2
python2 -m pip install virtualenv
python2 -m virtualenv py2venv
py2venv/bin/pip install ansible-review

echo "Port: $PORT"
exec python -m "$APP_MODULE"
