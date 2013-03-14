BEGIN;

DROP TABLE IF EXISTS collection;
CREATE TABLE collection (
    id int NOT NULL AUTO_INCREMENT
        PRIMARY KEY,
    user_id int(10) unsigned NOT NULL
        REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE,
    name varchar(32) NOT NULL,
    is_active tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB;

DROP TABLE IF EXISTS collection_has_song;
CREATE TABLE collection_has_song (
    collection_id int(11) NOT NULL
        REFERENCES collection(id) ON UPDATE CASCADE ON DELETE CASCADE,
    song_id int(11) NOT NULL
        REFERENCES song(id) ON UPDATE CASCADE ON DELETE CASCADE,
    position int DEFAULT NULL,
    last_played DATETIME DEFAULT NULL,
    PRIMARY KEY (collection_id, song_id)
) ENGINE=InnoDB;

COMMIT;

BEGIN;
    ALTER TABLE users ADD pinnedIp varchar(32);
COMMIT;

ALTER TABLE song ADD available TINYINT(1) DEFAULT 1;
