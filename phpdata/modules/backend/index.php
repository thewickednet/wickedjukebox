<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */

  $sock = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);

  socket_connect($sock, '127.0.0.1', 61111);

  if (socket_listen($sock) != "HELLO" ) {
     echo "socket_listen() failed: reason: " . socket_strerror($ret) . "\n";
  }

  switch($_GET['param']) {
    case "play":
      $command = "play\n";
      break;
    case "pause":
      $command = "pause\n";
      break;
    case "skip":
      $command = "skip\n";
      break;
    default:
      exit();
  } // switch



  socket_write($sock, $command);

  if (substr_count(socket_listen($sock), "OK") == 0) {
     echo "socket_listen() failed: reason: " . socket_strerror($ret) . "\n";
  }

  socket_close($sock);


  $queue = new Queue();

  $display = 0;
  $smarty->assign("QUEUE", Queue::getAll());
  $smarty->assign("QUEUE_TOTAL", Queue::getTotal());
  $smarty->display('queue.tpl');

?>
