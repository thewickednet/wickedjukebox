<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */



  switch($_GET['mode']){
    case "add":

      $songs = Album::getSongs($_GET['param']);

      foreach($songs as $song){
        $queue->add($song['song_id'], $song['track_no']);
      }

      break;
    case "del":
      include "modules/queue/album.php";
      break;
  } // switch


?>