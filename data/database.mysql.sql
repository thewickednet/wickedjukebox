--
-- Wicked jukebox database layout for MySQL
--

SET character_set_database="utf8";
SET collation_server="utf8_unicode_ci";
SET storage_engine="InnoDB";

DROP TABLE IF EXISTS setting;
DROP TABLE IF EXISTS genre;
DROP TABLE IF EXISTS channel_song_data;
DROP TABLE IF EXISTS channel_album_data;
DROP TABLE IF EXISTS queue;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS groups;
DROP TABLE IF EXISTS lastfm_queue;
DROP TABLE IF EXISTS dynamicPlaylist;
DROP TABLE IF EXISTS song_has_genre;
DROP TABLE IF EXISTS channel;
DROP TABLE IF EXISTS song;
DROP TABLE IF EXISTS album;
DROP TABLE IF EXISTS artist;

BEGIN;

   CREATE TABLE channel(
      id INTEGER UNSIGNED NOT NULL auto_increment PRIMARY KEY,
      name VARCHAR(32) NOT NULL UNIQUE,
      public BOOL NOT NULL DEFAULT TRUE,
      backend VARCHAR(64) NOT NULL,
      backend_params TEXT,
      ping DATETIME,
      active BOOL NOT NULL DEFAULT FALSE,
      status INTEGER
   );

   CREATE TABLE setting(
      var VARCHAR(32) NOT NULL PRIMARY KEY,
      value TEXT NOT NULL,
      comment TEXT,
      channel_id INTEGER UNSIGNED,
      INDEX (channel_id),
      FOREIGN KEY (channel_id) REFERENCES channel(id)
         ON UPDATE CASCADE ON DELETE RESTRICT
   );

   CREATE TABLE artist(
      id INTEGER UNSIGNED NOT NULL PRIMARY KEY,
      name VARCHAR(128) UNIQUE,
      added DATETIME NOT NULL
   );

   CREATE TABLE album(
      id INTEGER UNSIGNED NOT NULL PRIMARY KEY,
      artist_id INTEGER UNSIGNED NOT NULL,
      name VARCHAR(128),
      added DATETIME NOT NULL,
      downloaded INTEGER UNSIGNED NOT NULL DEFAULT 0,
      type VARCHAR(32),
      UNIQUE( id, artist_id),
      INDEX (artist_id),
      FOREIGN KEY (artist_id) REFERENCES artist(id)
         ON UPDATE CASCADE ON DELETE RESTRICT
   );

   CREATE TABLE genre(
      id INTEGER UNSIGNED NOT NULL PRIMARY KEY,
      name VARCHAR(128) UNIQUE,
      added DATETIME NOT NULL
   );

   CREATE TABLE song(
      id INTEGER UNSIGNED NOT NULL PRIMARY KEY,
      artist_id INTEGER UNSIGNED NOT NULL,
      album_id INTEGER UNSIGNED NOT NULL,
      track_no INTEGER(3) DEFAULT NULL,
      title VARCHAR(128),
      duration REAL, -- Duration in seconds
      year INTEGER(4) UNSIGNED,
      localpath VARCHAR(255) NOT NULL UNIQUE,
      downloaded INTEGER UNSIGNED DEFAULT 0,
      lastScanned DATETIME DEFAULT NULL,
      bitrate INTEGER(5),
      filesize INTEGER(32) UNSIGNED,
      checksum VARCHAR(14),
      lyrics TEXT,
      dirty BOOL DEFAULT FALSE,
      added DATETIME NOT NULL,

      INDEX (artist_id),
      FOREIGN KEY (artist_id) REFERENCES artist(id)
         ON UPDATE CASCADE ON DELETE RESTRICT,

      INDEX (album_id),
      FOREIGN KEY (album_id) REFERENCES album(id)
         ON UPDATE CASCADE ON DELETE RESTRICT

   );

   CREATE TABLE channel_song_data(
      channel_id INTEGER UNSIGNED NOT NULL,
      song_id INTEGER UNSIGNED NOT NULL,
      played     INTEGER UNSIGNED NOT NULL DEFAULT 0,
      voted      INTEGER UNSIGNED NOT NULL DEFAULT 0,
      skipped    INTEGER UNSIGNED NOT NULL DEFAULT 0,
      lastPlayed DATETIME,
      cost       INTEGER DEFAULT 5,
      PRIMARY KEY( channel_id, song_id ),

      INDEX(channel_id),
      FOREIGN KEY (channel_id) REFERENCES channel(id)
         ON UPDATE CASCADE ON DELETE RESTRICT,

      INDEX(song_id),
      FOREIGN KEY (song_id) REFERENCES song(id)
         ON UPDATE CASCADE ON DELETE RESTRICT

   );

   CREATE TABLE channel_album_data(
      channel_id INTEGER UNSIGNED NOT NULL,
      album_id INTEGER UNSIGNED NOT NULL,
      played INTEGER UNSIGNED NOT NULL DEFAULT 0,
      PRIMARY KEY( channel_id, album_id ),
      INDEX(channel_id),
      FOREIGN KEY (channel_id) REFERENCES channel(id)
         ON UPDATE CASCADE ON DELETE RESTRICT,

      INDEX(album_id),
      FOREIGN KEY (album_id) REFERENCES album(id)
         ON UPDATE CASCADE ON DELETE RESTRICT

   );

   CREATE TABLE groups (
     id INTEGER UNSIGNED NOT NULL PRIMARY KEY,
     title VARCHAR(32) NOT NULL,
     admin        INTEGER(1) NOT NULL default 0,
     nocredits    INTEGER NOT NULL default 0,
     queue_skip   INTEGER NOT NULL default 0,
     queue_remove INTEGER NOT NULL default 0,
     queue_add    INTEGER NOT NULL default 0
   );

   CREATE TABLE users (
      id  INTEGER UNSIGNED NOT NULL PRIMARY KEY,
      username VARCHAR(32) NOT NULL UNIQUE,
      cookie   VARCHAR(32) NOT NULL UNIQUE,
      password VARCHAR(32) NOT NULL,
      fullname VARCHAR(64) NOT NULL,
      credits  INTEGER(5) UNSIGNED NOT NULL,
      group_id INTEGER UNSIGNED NOT NULL,
      downloads INTEGER UNSIGNED NOT NULL DEFAULT 0,
      votes     INTEGER UNSIGNED NOT NULL DEFAULT 0,
      skips     INTEGER UNSIGNED NOT NULL DEFAULT 0,
      selects   INTEGER UNSIGNED NOT NULL DEFAULT 0,
      added DATETIME NOT NULL,

      INDEX(group_id),
      FOREIGN KEY (group_id) REFERENCES groups(id)
         ON UPDATE CASCADE ON DELETE RESTRICT

   );

   CREATE TABLE queue (
      id INTEGER UNSIGNED NOT NULL PRIMARY KEY,
      song_id INTEGER UNSIGNED NOT NULL,
      user_id INTEGER UNSIGNED DEFAULT NULL,
      channel_id INTEGER UNSIGNED NOT NULL,
      position INTEGER(5) DEFAULT 0,
      added DATETIME NOT NULL,

      INDEX(song_id),
      FOREIGN KEY (song_id) REFERENCES song(id)
         ON UPDATE CASCADE ON DELETE RESTRICT,

      INDEX(user_id),
      FOREIGN KEY (user_id) REFERENCES users(id)
         ON UPDATE CASCADE ON DELETE RESTRICT,

      INDEX(channel_id),
      FOREIGN KEY (channel_id) REFERENCES channel(id)
         ON UPDATE CASCADE ON DELETE RESTRICT

   );

   CREATE TABLE lastfm_queue(
      queue_id INTEGER UNSIGNED NOT NULL PRIMARY KEY,
      song_id INTEGER UNSIGNED NOT NULL,
      time_played DATETIME NOT NULL,
      INDEX(song_id),
      FOREIGN KEY (song_id) REFERENCES song(id)
         ON UPDATE CASCADE ON DELETE RESTRICT

   );

   CREATE TABLE dynamicPlaylist(
      id INTEGER UNSIGNED NOT NULL PRIMARY KEY,
      group_id INTEGER NOT NULL,
      label VARCHAR(64),
      query TEXT
   );

   CREATE TABLE song_has_genre(
      song_id INTEGER UNSIGNED NOT NULL
         REFERENCES song(id)
            ON UPDATE CASCADE
            ON DELETE RESTRICT,
      genre_id INTEGER UNSIGNED NOT NULL
         REFERENCES genre(id)
            ON UPDATE CASCADE
            ON DELETE RESTRICT,
      PRIMARY KEY (song_id, genre_id),
      INDEX(song_id),
      FOREIGN KEY (song_id) REFERENCES song(id)
         ON UPDATE CASCADE ON DELETE RESTRICT,

      INDEX(genre_id),
      FOREIGN KEY (genre_id) REFERENCES genre(id)
         ON UPDATE CASCADE ON DELETE RESTRICT
   );
COMMIT;
