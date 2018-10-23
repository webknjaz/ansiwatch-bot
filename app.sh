#! /usr/bin/env bash

git --version

{
    >&2 echo Starting to set up python2 env for ansible-review asynchronously...
    curl https://bootstrap.pypa.io/get-pip.py | python2 - --user
    python2 -m pip install virtualenv --user
    python2 -m virtualenv py2venv
    py2venv/bin/pip install ansible-review
} &

echo "Port: $PORT"
exec python -m "$APP_MODULE"
