#!/bin/bash

docker run \
    --link jukebox-mysql:mysql \
    -v $(pwd):/data \
    -v $(pwd)/docker/overlay/etc/wicked/wickedjukebox:/etc/wicked/wickedjukebox \
    -v $(pwd)/docker/overlay/etc/icecast2:/etc/icecast2 \
    -v /home/exhuma/mp3:/var/mp3/Tagged \
    -ti exhuma/jukeboxbe:latest \
    /bin/bash
