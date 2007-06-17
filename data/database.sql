DROP TABLE IF EXISTS setting;
DROP TABLE IF EXISTS channel;
DROP TABLE IF EXISTS playmode;
DROP TABLE IF EXISTS artist;
DROP TABLE IF EXISTS album;
DROP TABLE IF EXISTS genre;
DROP TABLE IF EXISTS song;
DROP TABLE IF EXISTS channel_song_data;
DROP TABLE IF EXISTS channel_album_data;
DROP TABLE IF EXISTS queue;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS groups;
DROP TABLE IF EXISTS lastfm_queue;
DROP TABLE IF EXISTS dynamicPlaylist;
DROP TABLE IF EXISTS song_has_genre;

----------------------------------------------------------------------------

BEGIN;

CREATE TABLE playmode(
   id INTEGER NOT NULL PRIMARY KEY,
   name VARCHAR(32) NOT NULL
      CONSTRAINT unique_playmode UNIQUE
);

CREATE TABLE channel(
   id INTEGER NOT NULL PRIMARY KEY,
   name VARCHAR(32) NOT NULL
      CONSTRAINT unique_channel UNIQUE,
   public INTEGER(1) NOT NULL DEFAULT 1,
   backend VARCHAR(64) NOT NULL,
   backend_params TEXT,
   ping DATETIME,
   active INTEGER(1) NOT NULL DEFAULT 0,
   status INTEGER,
   playmode INTEGER
      REFERENCES playmode(id)
         ON DELETE RESTRICT
         ON UPDATE CASCADE
);

CREATE TABLE setting(
   var VARCHAR(32) NOT NULL PRIMARY KEY,
   value TEXT NOT NULL,
   comment TEXT,
   channel_id INTEGER
      REFERENCES channel(id)
         ON UPDATE CASCADE
         ON DELETE RESTRICT
);

CREATE TABLE artist(
   id INTEGER NOT NULL PRIMARY KEY,
   name VARCHAR(128) UNIQUE,
   added DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE album(
   id INTEGER NOT NULL PRIMARY KEY,
   artist_id INTEGER NOT NULL
      REFERENCES artist(id)
         ON UPDATE CASCADE
         ON DELETE RESTRICT,
   name VARCHAR(128),
   added DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
   downloaded INTEGER NOT NULL DEFAULT 0,
   type VARCHAR(32),
   UNIQUE( id, artist_id)
);

CREATE TABLE genre(
   id INTEGER NOT NULL PRIMARY KEY,
   name VARCHAR(128) UNIQUE,
   added DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE song(
   id INTEGER NOT NULL PRIMARY KEY,
   artist_id INTEGER NOT NULL
      REFERENCES artist(id)
         ON UPDATE CASCADE
         ON DELETE RESTRICT,
   album_id INTEGER NOT NULL
      REFERENCES album(id)
         ON UPDATE CASCADE
         ON DELETE RESTRICT,
   track_no INTEGER(3) DEFAULT NULL,
   title VARCHAR(128),
   duration REAL, -- Duration in seconds
   year INTEGER(4),
   localpath TEXT NOT NULL UNIQUE,
   downloaded INTEGER DEFAULT 0,
   lastScanned DATETIME DEFAULT NULL DEFAULT CURRENT_TIMESTAMP,
   bitrate INTEGER(5),
   filesize INTEGER(32),
   checksum VARCHAR(14),
   lyrics TEXT,
   dirty INTEGER(1) DEFAULT 0,
   added DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE channel_song_data(
   channel_id INTEGER NOT NULL
      REFERENCES channel(id)
         ON UPDATE CASCADE
         ON DELETE RESTRICT,
   song_id INTEGER NOT NULL
      REFERENCES song(id)
         ON UPDATE CASCADE
         ON DELETE RESTRICT,
   played     INTEGER NOT NULL DEFAULT 0,
   voted      INTEGER NOT NULL DEFAULT 0,
   skipped    INTEGER NOT NULL DEFAULT 0,
   lastPlayed DATETIME DEFAULT CURRENT_TIMESTAMP,
   cost       INTEGER DEFAULT 5,
   PRIMARY KEY( channel_id, song_id )
);

CREATE TABLE channel_album_data(
   channel_id INTEGER NOT NULL
      REFERENCES channel(id)
         ON UPDATE CASCADE
         ON DELETE RESTRICT,
   album_id INTEGER NOT NULL
      REFERENCES album(id)
         ON UPDATE CASCADE
         ON DELETE RESTRICT,
   played     INTEGER NOT NULL DEFAULT 0,
   PRIMARY KEY( channel_id, album_id )
);

CREATE TABLE groups (
  id INTEGER NOT NULL PRIMARY KEY,
  title VARCHAR(32) NOT NULL,
  admin        INTEGER(1) NOT NULL default 0,
  nocredits    INTEGER NOT NULL default 0,
  queue_skip   INTEGER NOT NULL default 0,
  queue_remove INTEGER NOT NULL default 0,
  queue_add    INTEGER NOT NULL default 0
);

CREATE TABLE users (
   id  INTEGER NOT NULL PRIMARY KEY,
   username VARCHAR(32) NOT NULL UNIQUE,
   cookie   VARCHAR(32) NOT NULL UNIQUE,
   password VARCHAR(32) NOT NULL,
   fullname VARCHAR(64) NOT NULL,
   credits  INTEGER(5) NOT NULL,
   group_id INTEGER(3) NOT NULL
       REFERENCES groups(id)
         ON UPDATE CASCADE
         ON DELETE RESTRICT,
   downloads INTEGER NOT NULL DEFAULT 0,
   votes     INTEGER NOT NULL DEFAULT 0,
   skips     INTEGER NOT NULL DEFAULT 0,
   selects   INTEGER NOT NULL DEFAULT 0,
   added DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE queue (
   id INTEGER NOT NULL PRIMARY KEY,
   song_id INTEGER NOT NULL
      REFERENCES song(id)
         ON UPDATE CASCADE
         ON DELETE RESTRICT,
   user_id INTEGER DEFAULT NULL
      REFERENCES users(id)
         ON UPDATE CASCADE
         ON DELETE RESTRICT,
   channel_id INTEGER NOT NULL
      REFERENCES channel(id)
         ON UPDATE CASCADE
         ON DELETE RESTRICT,
   position INTEGER(5) DEFAULT 0,
   added DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE lastfm_queue(
   queue_id INTEGER NOT NULL PRIMARY KEY,
   song_id INTEGER NOT NULL
      REFERENCES song(id)
         ON UPDATE CASCADE
         ON DELETE RESTRICT,
   time_played DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE dynamicPlaylist(
   id INTEGER NOT NULL PRIMARY KEY,
   group_id INTEGER NOT NULL,
   label VARCHAR(64),
   query TEXT
);

CREATE TABLE song_has_genre(
   song_id INTEGER NOT NULL
      REFERENCES song(id)
         ON UPDATE CASCADE
         ON DELETE RESTRICT,
   genre_id INTEGER NOT NULL
      REFERENCES genre(id)
         ON UPDATE CASCADE
         ON DELETE RESTRICT,
   PRIMARY KEY (song_id, genre_id)
);

COMMIT;

