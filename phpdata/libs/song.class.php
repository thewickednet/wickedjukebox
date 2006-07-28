<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */

class Song {

  function getById($id = 0){

    $db = ezcDbInstance::get();

    $stmt = $db->prepare("SELECT * FROM songs, artists WHERE songs.artist_id = artists.artist_id AND songs.song_id = ? LIMIT 1");
    $stmt->execute(array("$id"));

    $result = $stmt->fetchAll();

    return $result[0];
  }


}

?>