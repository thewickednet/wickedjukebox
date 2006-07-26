<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */

class Song {

  function getById($id = ""){

    $db = ezcDbInstance::get();

    $stmt = $db->prepare("SELECT * FROM songs, artists WHERE songs.artist_id = artists.artist_id AND songs.song_id = ?");
    $stmt->execute(array("$id"));

    return $stmt->fetchAll();
  }
}

?>