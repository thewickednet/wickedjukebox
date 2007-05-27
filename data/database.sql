DROP TABLE setting;
DROP TABLE channel;
DROP TABLE playmode;

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
   backend VARCHAR(64) NOT NULL,
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

COMMIT;

------------------------------------------------------------------------------
-- DATA
------------------------------------------------------------------------------

BEGIN;
   INSERT INTO playmode (name) VALUES ( 'strictQueue' );
   INSERT INTO channel  (name,backend,playmode) VALUES ( 'exhuma', 'mpd', 1 );
   INSERT INTO setting  (var, value, comment) VALUES ( 'mediadir', '/mp3', 'Folders that contain the media files. Separated by commas' );
COMMIT;
