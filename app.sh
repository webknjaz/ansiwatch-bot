#! /usr/bin/env bash

git --version

{
    >&2 echo Downloading git-new-workdir script asynchronously...
    mkdir -pv bin/
    wget -O bin/git-new-workdir https://raw.githubusercontent.com/git/git/master/contrib/workdir/git-new-workdir
    chmod +x bin/git-new-workdir
} &

echo "Port: $PORT"
exec python -m "$APP_MODULE"
