<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */


  $song = Song::getById($_GET['param']);
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

?>