<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */

class Search {

  function findAny($pattern){

    $db = ezcDbInstance::get();

    $stmt = $db->prepare("SELECT songs_id.song_id FROM songs, artists, albums WHERE albums.album_id = songs.song_id AND songs.artist_id = artists.artist_id AND (albums.title LIKE ? OR songs.title LIKE ? OR artists.name LIKE ?) ORDER BY artists.artist_name, albums.album_title, songs.track_no, songs.title");
    $stmt->execute(array("%$pattern%", "%$pattern%", "%$pattern%"));

    return $stmt->fetchAll();
  }


  function findArtist($pattern){

    $db = ezcDbInstance::get();

    $stmt = $db->prepare("SELECT songs_id.song_id FROM songs, artists, albums WHERE albums.album_id = songs.song_id AND songs.artist_id = artists.artist_id AND artists.name LIKE ? ORDER BY artists.artist_name, albums.album_title, songs.track_no, songs.title");
    $stmt->execute(array("%$pattern%"));

    return $stmt->fetchAll();
  }


  function findAlbum($pattern){

    $db = ezcDbInstance::get();

    $stmt = $db->prepare("SELECT songs_id.song_id FROM songs, artists, albums WHERE albums.album_id = songs.song_id AND songs.artist_id = artists.artist_id AND albums.title LIKE ? ORDER BY artists.artist_name, albums.album_title, songs.track_no, songs.title");
    $stmt->execute(array("%$pattern%"));

    return $stmt->fetchAll();
  }


  function findSong($pattern){

    $db = ezcDbInstance::get();

    $stmt = $db->prepare("SELECT songs_id.song_id FROM songs, artists, albums WHERE albums.album_id = songs.song_id AND songs.artist_id = artists.artist_id AND songs.title LIKE ? ORDER BY artists.artist_name, albums.album_title, songs.track_no, songs.title");
    $stmt->execute(array("%$pattern%"));

    return $stmt->fetchAll();
  }

}

?>