#!/usr/bin/env bash

export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y \
    python-pip \
    vim \
    python-dev \
    libmysqlclient-dev \
    build-essential \
    libshout-dev \
    icecast2

pip install virtualenv

[ -d jukebox-env ] || virtualenv jukebox-env

./jukebox-env/bin/pip install -r /vagrant/requirements.txt
./jukebox-env/bin/pip install -e /vagrant

chorn -R vagrant:vagrant jukebox-env
