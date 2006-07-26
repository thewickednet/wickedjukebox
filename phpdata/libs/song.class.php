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

    $stmt = $db->prepare("SELECT * FROM songs, artists WHERE songs.artist_id = artists.artist_id AND songs.song_id = ?");
    $stmt->execute(array("$id"));

    return $stmt->fetchAll();
  }

  function download($id = 0){

    $song = self::getById($id);
    $song = $song[0];

    $filename = basename($song['localpath']);
    $extension = split("\.", $filename);
    $extension = $extension[count($extension)-1];

    $filename = sprintf("%s - %s.%s", $song['name'], $song['title'], $extension );
    $filename = str_replace(" ", "_", $filename);


    $mime = mime_content_type($song['localpath']);
    header('Content-type: ' . $mime);
    header("Content-length: ".filesize($song['localpath']));
    header('Content-Disposition: attachment; filename="'.$filename.'"');
    $fp = fopen($song['localpath'], "r");
    fpassthru($fp);
    fclose($fp);
    exit();

  }



}

?>