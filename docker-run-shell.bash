#!/bin/bash

docker run --link jukebox-mysql:mysql -ti exhuma/jukeboxbe:latest /bin/bash
