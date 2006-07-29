<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */


  $song = Song::getById($_GET['param']);

  $filename = basename($song['localpath']);

//  if (file_exists($filename)) {

    $extension = split("\.", $filename);
    $extension = $extension[count($extension)-1];

    $filename = sprintf("%s - %s.%s", $song['name'], $song['title'], $extension );
    $filename = str_replace(" ", "_", $filename);

    Song::countDownload($_GET['param']);
    User::countDownload($userinfo['user_id']);

    $mime = mime_content_type($song['localpath']);
    header('Content-type: ' . $mime);
    header("Content-length: ".filesize($song['localpath']));
    header('Content-Disposition: attachment; filename="'.$filename.'"');
    $fp = fopen($song['localpath'], "r");
    fpassthru($fp);
    fclose($fp);
    exit();

/*  } else {
    die("file does not exist.");
  }
*/

?>