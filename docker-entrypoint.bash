#!/bin/bash

#
# This file should be executed inside the container. It starts the necessary
# services and gets the container up and running.
#
if [[ "${DEV}" == "1" ]]; then
    cd /data && /opt/jukebox/bin/alembic upgrade head
fi

echo Starting icecast service ...
icecast2 -b -c /etc/icecast2/icecast.xml

echo giving icecast 3s to startup
sleep 3
echo Icecast startup completed!

echo Starting jukebox...
/opt/jukebox/bin/run-channel -c wicked
