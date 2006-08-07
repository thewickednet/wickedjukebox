<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */


class Player {

  function getStatus($channel_id = 1) {
    $db = ezcDbInstance::get();

    $q = $db->createSelectQuery();
    $e = $q->expr;
    $q->select( '*' )->from( 'players' )->where( $e->eq( 'channel_id', $q->bindValue( $channel_id ) ) );

    $stmt = $q->prepare();
    $stmt->execute();

    $rows = $stmt->fetchAll();
    if (count($rows) == 0)
      return array();
    else {
      $row = $rows[0];
      $song = Song::getById($row['song_id']);
      if (isset($song['album_id'])) {
        $row['album_info'] = Album::getById($song['album_id']);
        $row['cover'] = Album::hasCover($song['album_id']);
      }
      $row = array_merge($row, $song);
    }
    return $row;
  }


  function getStatusFromSocket() {

    $result = array();

    $sock = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);

    $host = Setting::get("daemon_boundHost");
    $port = Setting::get("daemon_port");

    socket_connect($sock, $host, $port);

    $hello = socket_read($sock, 512);

    socket_write($sock, "player_status\n");
    $reader = socket_read($sock, 512);
    $player_status = split(":", $reader);

    socket_write($sock, "now_playing\n");
    $reader = socket_read($sock, 512);
    $now_playing = split(":", $reader);

    socket_close($sock);


    $result['player_status'] = $player_status;
    $result['now_playing'] = $now_playing;

    if ($result['now_playing'][1] != '0') {
      $song = Song::getById($result['now_playing'][1]);
      $result['song_info'] = $song;
      if (isset($song['album_id'])) {
        $result['album_info'] = Album::getById($song['album_id']);
        $result['cover'] = Album::hasCover($song['album_id']);
      }
    }
    return $result;
  }

}
?>
