<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */

class Artist {




  function getAlphaIndex(){

    $db = ezcDbInstance::get();

    $res = $db->query("SELECT DISTINCT SUBSTRING(name,1,1) AS alpha FROM artists ORDER BY alpha");
    return $res->fetchAll();
  }

  function getByAlpha($alpha = "A"){

    $db = ezcDbInstance::get();

    $stmt = $db->prepare("SELECT * FROM artists WHERE name LIKE ? ORDER BY name");
    $stmt->execute(array("$alpha%"));

    return $stmt->fetchAll();
  }

  function getById($id = ""){

    $db = ezcDbInstance::get();

    $stmt = $db->prepare("SELECT * FROM artists WHERE artist_id = ?");
    $stmt->execute(array("$id"));

    return $stmt->fetchAll();
  }

  function getSongs($id = 0){

    $db = ezcDbInstance::get();

    $results = array();

    $stmt = $db->prepare("SELECT *, songs.title AS song, albums.title AS album FROM songs, albums WHERE songs.album_id = albums.album_id AND songs.artist_id = ? ORDER BY albums.title, track_no, song");
    $stmt->execute(array("$id"));
    return $stmt->fetchAll();
  }

}


?>