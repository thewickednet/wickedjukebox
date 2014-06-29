#!/bin/bash

[ -d jukebox-env ] || virtualenv jukebox-env

./jukebox-env/bin/pip install -r /vagrant/requirements.txt
./jukebox-env/bin/pip install -e /vagrant

(cd /vagrant && /home/vagrant/jukebox-env/bin/alembic upgrade head)
