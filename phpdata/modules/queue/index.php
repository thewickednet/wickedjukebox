<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */


  $queue = new Queue();

  switch($_GET['module']){
    case "song":
      include "modules/queue/song.php";
      break;
    case "album":
      include "modules/queue/album.php";
      break;
    default:
      header("Location: index.php");
  } // switch

  if ($_GET['ajax']) {
    $display = 0;
    $smarty->assign("QUEUE", Queue::getAll());
    $smarty->assign("QUEUE_TOTAL", Queue::getTotal());
    $smarty->display('queue.tpl');
  }

?>