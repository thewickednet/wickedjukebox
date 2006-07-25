<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */


class Album {



  function getAlphaIndex(){

    $db = ezcDbInstance::get();

    $res = $db->query("SELECT DISTINCT SUBSTRING(title,1,1) AS alpha FROM albums ORDER BY alpha");
    return $res->fetchAll();
  }

  function getByAlpha($alpha = "A"){

    $db = ezcDbInstance::get();

    $stmt = $db->prepare("SELECT * FROM albums WHERE title LIKE ? ORDER BY title");
    $stmt->execute(array("$alpha%"));

    return $stmt->fetchAll();
  }

  function getById($id = ""){

    $db = ezcDbInstance::get();

    $stmt = $db->prepare("SELECT * FROM albums WHERE album_id = ?");
    $stmt->execute(array("$id"));

    return $stmt->fetchAll();
  }

  function getSongs($id = 0){

    $db = ezcDbInstance::get();

    $results = array();

    $stmt = $db->prepare("SELECT *, songs.title AS song, albums.title AS album FROM songs, albums WHERE songs.album_id = albums.album_id AND albums.album_id = ? ORDER BY albums.title, track_no, song");
    $stmt->execute(array("$id"));
    return $stmt->fetchAll();
  }



}



?>