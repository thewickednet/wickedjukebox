#!/bin/bash

echo WARNING: This is INSECURE! It is meant for development only!
echo
echo Database Name: jukebox
echo Database User: jukebox
echo Database Password: jukebox
echo Database Root Password: rootpw
echo Database Host: localhost
echo "Database Port: Dynamic (run 'docker ps' to find out)"
echo
echo Data and container are *not* persistent!
echo
echo Press any key to continue, CTRL+C to abort...
read

CONTAINER_ID=$(docker run \
    --rm \
    --name jukeboxdb \
    -e MARIADB_DATABASE=jukebox \
    -e MARIADB_USER=jukebox \
    -e MARIADB_PASSWORD=jukebox \
    -e MARIADB_ROOT_PASSWORD=rootpw \
    -P \
    -d \
    mariadb:10
)

echo
echo "Port Bindings:"
echo
docker inspect \
    --format='{{range $p, $conf := .NetworkSettings.Ports}} {{$p}} -> {{(index $conf 0).HostPort}} {{end}}' \
    ${CONTAINER_ID}

echo
echo Stopping the container will nuke the data!
echo
echo To stop, run:
echo "   docker stop ${CONTAINER_ID}"
