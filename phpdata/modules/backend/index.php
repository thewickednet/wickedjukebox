<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */

  $sock = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);

  $host = Setting::get("daemon_boundHost");
  $port = Setting::get("daemon_port");

  socket_connect($sock, $host, $port);

  if (socket_read($sock) != "HELLO" ) {
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

  if (substr_count(socket_read($sock), "OK") == 0) {
     echo "socket_listen() failed: reason: " . socket_strerror($ret) . "\n";
  }

  socket_close($sock);


  $queue = new Queue();

  $display = 0;
  $smarty->assign("QUEUE", Queue::getAll());
  $smarty->assign("QUEUE_TOTAL", Queue::getTotal());
  $smarty->display('queue.tpl');

?>
