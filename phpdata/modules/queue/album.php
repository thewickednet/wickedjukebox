<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */


  switch($_GET['mode']){
    case "add":

      if ($permissions['queue_add'] == '1') {
        $songs = Album::getSongs($_GET['param']);

        foreach($songs as $song){
          $queue->add($song['song_id'], $song['track_no']);
          //Song::countPlay($song['song_id']);
          //User::countPlay($userinfo['user_id']);
        }

        Album::countPlay($_GET['param']);
      } else {
        die("no permissions for this action.");
      }

      break;
  } // switch

?>
