<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */


class Queue {


  function getAll($channel = 1){
    $db = ezcDbInstance::get();

    $q = $db->createSelectQuery();
    $e = $q->expr;
    $q->select( '*' )
      ->from( 'queue', 'songs', 'users' )
      ->where( 'users.user_id', 'queue.user_id' )
      ->where( 'songs.song_id', 'queue.song_id' )
      ->where( $e->eq( 'channel_id', $q->bindValue( $channel ) ) );
    $stmt = $q->prepare();
    $stmt->execute();
    $rows = $stmt->fetchAll();
    return $rows;

  }


}


?>