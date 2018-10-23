#! /usr/bin/env bash

git --version

{
    >&2 echo Downloading git-new-workdir script asynchronously...
    mkdir -pv bin/
    wget -O bin/git-new-workdir https://raw.githubusercontent.com/git/git/master/contrib/workdir/git-new-workdir
    chmod +x bin/git-new-workdir
} &

{
    >&2 echo Starting to set up python2 env for ansible-review asynchronously...
    curl https://bootstrap.pypa.io/get-pip.py | python2 - --user
    python2 -m pip install virtualenv --user
    python2 -m virtualenv py2venv
    py2venv/bin/pip install ansible-review
} &

echo "Port: $PORT"
exec python -m "$APP_MODULE"
