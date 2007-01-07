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
        $queue->add($_GET['param']);
        Song::countPlay($_GET['param']);

        User::countPlay($userinfo['user_id']);

        if ( $permissions['nocredits'] != '1') {
           // TODO: make this dependent on song-length
           User::pay($userinfo['user_id'], 5);
        }

      } else {
        die("no permissions for this action.");
      }

      break;
    case "del":

//      if ($permissions['queue_remove'] == '1') {
        $queue->del($_GET['param']);
        if ( $permissions['nocredits'] != '1') {
           // TODO: make this dependent on song-length
           User::reward($userinfo['user_id'], 5);
        }

//      } else {
//        die("no permissions for this action.");
//      }

      break;
  } // switch


?>
