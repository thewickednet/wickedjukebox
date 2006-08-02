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

}


?>