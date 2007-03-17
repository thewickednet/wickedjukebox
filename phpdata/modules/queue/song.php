<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */



  $song = Song::getById( $_GET['param'] );
  $songMinutes = floor($song['seconds'] / 60);
  switch($_GET['mode']){
    case "add":

      if ($permissions['queue_add'] == '1') {

        if ( $permissions['nocredits'] != '1') {
           if ( $userinfo['credits'] < $songMinutes ){
              die('not enough credits');
           }
           User::pay($userinfo['user_id'], $songMinutes );
        }

        $queue->add($_GET['param']);
        Song::countPlay($_GET['param']);

        User::countPlay($userinfo['user_id']);

      } else {
        die("no permissions for this action.");
      }

      break;
    case "del":

//      if ($permissions['queue_remove'] == '1') {
        $queue->del($_GET['param']);
        if ( $permissions['nocredits'] != '1') {
           User::reward($userinfo['user_id'], $songMinutes );
        }

//      } else {
//        die("no permissions for this action.");
//      }

      break;
  } // switch


?>
