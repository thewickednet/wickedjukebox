#!/bin/bash
docker run -it --link jukebox-mysql:mysql --rm mysql:5 sh -c 'exec mysql -h"$MYSQL_PORT_3306_TCP_ADDR" -P"$MYSQL_PORT_3306_TCP_PORT" -uroot -p"$MYSQL_ENV_MYSQL_ROOT_PASSWORD"'


# CREATE USER 'jukebox'@'%' IDENTIFIED BY 'jukebox';
# GRANT ALL PRIVILEGES ON *.* TO 'jukebox'@'%';
# FLUSH PRIVILEGES
