DROP TABLE IF EXISTS setting;
DROP TABLE IF EXISTS channel;
DROP TABLE IF EXISTS playmode;
DROP TABLE IF EXISTS artist;
DROP TABLE IF EXISTS album;
DROP TABLE IF EXISTS genre;
DROP TABLE IF EXISTS song;
DROP TABLE IF EXISTS channel_song_data;

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
   channel INTEGER
      REFERENCES channel(id)
         ON UPDATE CASCADE
         ON DELETE RESTRICT
);

CREATE TABLE artist(
   id INTEGER NOT NULL PRIMARY KEY,
   name VARCHAR(128),
   added DATETIME NOT NULL
);

CREATE TABLE album(
   id INTEGER NOT NULL PRIMARY KEY,
   name VARCHAR(128),
   added DATETIME NOT NULL,
   artist_id INTEGER NOT NULL
      REFERENCES artist(id)
         ON UPDATE CASCADE
         ON DELETE RESTRICT,
   downloaded INTEGER NOT NULL DEFAULT 0,
   type VARCHAR(32)
);

CREATE TABLE genre(
   id INTEGER NOT NULL PRIMARY KEY,
   name VARCHAR(128),
   added DATETIME NOT NULL
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
   genre_id INTEGER NOT NULL
      REFERENCES genre(id)
         ON UPDATE CASCADE
         ON DELETE RESTRICT,
   track_no INTEGER(3) DEFAULT NULL,
   title VARCHAR(128),
   duration INTEGER(4),  -- Duration in seconds
   year INTEGER(4),
   localpath TEXT NOT NULL,
   downloaded INTEGER DEFAULT 0,
   lastScanned DATETIME DEFAULT NULL,
   bitrate INTEGER(5),
   filesize INTEGER(32),
   checksum VARCHAR(14),
   lyrics TEXT,
   dirty INTEGER(1) DEFAULT 0,
   added DATETIME NOT NULL
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
   lastPlayed DATETIME DEFAULT NULL,
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

COMMIT;

------------------------------------------------------------------------------
-- DATA
------------------------------------------------------------------------------

BEGIN;
   INSERT INTO playmode (name) VALUES ( 'strictQueue' );
   INSERT INTO channel  (name,backend,playmode) VALUES ( 'exhuma', 'mpd', 1 );
   INSERT INTO setting  (var, value, comment) VALUES ( 'mediadir', '/mp3', 'Folders that contain the media files. Separated by commas' );
COMMIT;
