<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */



  switch($_GET['mode']){
    case "add":

      $queue->add($_GET['param']);

      break;
    case "del":
      $queue->del($_GET['param']);
      break;
  } // switch


?>