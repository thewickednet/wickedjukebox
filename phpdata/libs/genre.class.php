<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */

class Genre {

  function getById($id = 0){

    $db = ezcDbInstance::get();

    $stmt = $db->prepare("SELECT * FROM genres WHERE genre_id = ? LIMIT 1");
    $stmt->execute(array("$id"));
    $result = $stmt->fetchAll();
    return $result[0];
  }

  function getAll() {


    $cache = ezcCacheManager::getCache('long');

    $cache_id = "genres_alpha_index";

    if ( ( $results = $cache->restore( $cache_id ) ) === false ) {

    $db = ezcDbInstance::get();

    $results = array();

    $q = $db->createSelectQuery();
    $e = $q->expr;
    $q->select( '*' )->from( 'genres' )
      ->orderBy( 'name' );
    $stmt = $q->prepare();
    $stmt->execute();

    while ($row = $stmt->fetch())
      $results[$row['genre_id']] = $row['name'];
      $cache->store( $cache_id, $results );
    }

    return $results;

  }

  function getAvailable(){

    $db = ezcDbInstance::get();

    $stmt = $db->prepare("SELECT * FROM genres WHERE genre_id = (SELECT DISTINCT genre_id FROM songs) ORDER BY name");
    $stmt->execute();

    return $stmt->fetchAll();

  }

  function getSongs($id = 0){

    $cache = ezcCacheManager::getCache('short');

    $cache_id = sprintf("genres_songs_%d", $id);

    if ( ( $results = $cache->restore( $cache_id ) ) === false ) {

      $db = ezcDbInstance::get();

      $results = array();

      $stmt = $db->prepare("SELECT *, songs.title AS song, albums.title AS album FROM songs, albums, artists WHERE songs.artist_id = artists.artist_id AND songs.album_id = albums.album_id AND songs.genre_id = ? ORDER BY artists.name, albums.title, track_no, song");
      $stmt->execute(array("$id"));
      $results = $stmt->fetchAll();
      $cache->store( $cache_id, $results );

    }

    return $results;
  }



}

?>