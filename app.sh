#! /usr/bin/env bash

git --version

{
    >&2 echo Downloading git-new-workdir script asynchronously...
    mkdir -pv bin/
    wget -O bin/git-new-workdir https://raw.githubusercontent.com/git/git/master/contrib/workdir/git-new-workdir
    chmod +x bin/git-new-workdir
} &

{
    >&2 echo Upgrading git asynchronously...
    wget -O - https://setup.ius.io | sudo bash -
    sudo yum install -y git2u
} &

>&2 echo "Port: $PORT"
>&2 echo Waiting for pre-requisites install to complete...
wait
exec python -m "$APP_MODULE"
