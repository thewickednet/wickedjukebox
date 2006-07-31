<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */

class Artist {

  function getAlphaIndex(){

    $cache = ezcCacheManager::getCache('long');

    $cache_id = "artist_alpha_index";

    if ( ( $results = $cache->restore( $cache_id ) ) === false ) {

      $db = ezcDbInstance::get();

      $res = $db->query("SELECT DISTINCT SUBSTRING(name,1,1) AS alpha FROM artists ORDER BY alpha");
      $results = $res->fetchAll();
      $cache->store( $cache_id, $results );

    }


    return $results;
  }

  function getByAlpha($alpha = "A"){

    $cache = ezcCacheManager::getCache('short');

    $cache_id = sprintf("artist_alpha_index_%s", $alpha);

    if ( ( $results = $cache->restore( $cache_id ) ) === false ) {

      $db = ezcDbInstance::get();

      $stmt = $db->prepare("SELECT * FROM artists WHERE name LIKE ? ORDER BY name");
      $stmt->execute(array("$alpha%"));
      $results = $stmt->fetchAll();
      $cache->store( $cache_id, $results );

    }

    return $results;
  }

  function getById($id = ""){

    $db = ezcDbInstance::get();

    $stmt = $db->prepare("SELECT * FROM artists WHERE artist_id = ? LIMIT 1");
    $stmt->execute(array("$id"));
    $result = $stmt->fetchAll();

    return $result[0];
  }

  function getByName($name){

    $db = ezcDbInstance::get();

    $stmt = $db->prepare("SELECT * FROM artists WHERE name = ? LIMIT 1");
    $stmt->execute(array("$name"));
    $result = $stmt->fetchAll();

    return $result[0];
  }

  function add($name){

    $db = ezcDbInstance::get();

    $q = $db->createInsertQuery();
    $q->insertInto( 'artists' )
      ->set( 'name', $q->bindValue( $name ) )
      ->set( 'added', $q->bindValue(  strftime("%Y-%m-%d %H:%M:%S") ) );
    $stmt = $q->prepare();
    $stmt->execute();

    return $db->lastInsertId();

  }

  function getSongs($id = 0){

    $cache = ezcCacheManager::getCache('short');

    $cache_id = sprintf("browse_artists_%s", $id);

    if ( ( $results = $cache->restore( $cache_id ) ) === false ) {

      $db = ezcDbInstance::get();

      $results = array();

      $stmt = $db->prepare("SELECT *, songs.title AS song, albums.title AS album FROM songs, albums WHERE songs.album_id = albums.album_id AND songs.artist_id = ? ORDER BY albums.title, track_no, song");
      $stmt->execute(array("$id"));
      $results = $stmt->fetchAll();

      $cache->store( $cache_id, $results );

    }


    return $results;
  }


  function hasCover($id = 0){

    $result = "";

    $songs = self::getSongs($id);
    foreach($songs as $song) {

      $check = dirname($song['localpath']) . '/../folder.jpg';
      if (file_exists($check)) {
        return $check;
      }
    }

    return "";

  }

  function showCover($original){

    $w_max = 200;
    $h_max = 200;

    $src_size = getimagesize($original);

    $w_orig = $src_size[0];
    $h_orig = $src_size[1];

    $proportion = $src_size[0] / $src_size[1];
    $w_potentiel = $h_max * $proportion;
    $h_potentiel = $w_max / $proportion;
    if ($w_potentiel <= $w_max) {
      $format_final_w = $w_potentiel;
      $format_final_h = $h_max;
    } elseif ($h_potentiel <= $h_max) {
      $format_final_w = $w_max;
      $format_final_h = $h_potentiel;
    }

    $image_p = imagecreatetruecolor($format_final_w, $format_final_h);
    $image = imagecreatefromjpeg($original);
    imagecopyresampled($image_p, $image, 0, 0, 0, 0, $format_final_w, $format_final_h, $w_orig, $h_orig);
    header("Content-type: image/jpeg");
    imagejpeg($image_p, "", 80);
    exit();
  }


}


?>