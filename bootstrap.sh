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
    mysql-server \
    icecast2

pip install virtualenv

mysql -u root -e "CREATE DATABASE IF NOT EXISTS jukebox CHARACTER SET utf8 COLLATE 'utf8_general_ci'"
echo "Created database 'jukebox'"
mysql -u root -e "GRANT ALL PRIVILEGES ON jukebox.* TO 'jukebox'@'localhost' IDENTIFIED BY 'jukebox'; FLUSH PRIVILEGES;"
echo "Created database user 'jukebox' with password 'jukebox'"
