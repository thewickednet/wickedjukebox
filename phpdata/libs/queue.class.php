<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */


class Queue {

  var $channel_id = 1;
  var $user_id = 0;


  function getAll($channel = 1) {
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


  function add($song_id, $position = 0) {
    $db = ezcDbInstance::get();

    $q = $db->createInsertQuery();
    $q->insertInto( 'queue' )
      ->set( 'song_id', $q->bindValue( $song_id ) )
      ->set( 'channel_id', $q->bindValue( $channel_id ) )
      ->set( 'user_id', $q->bindValue( $user_id ) )
      ->set( 'position', $q->bindValue( $position ) );
    $stmt = $q->prepare();
    $stmt->execute();

  }

  function del($queue_id) {
    $db = ezcDbInstance::get();

    $q = $db->createDeleteQuery();
    $q->deleteFrom( 'queue' )
      ->where( $e->eq( 'queue_id', $q->bindValue( $queue_id ) ) );

    $stmt = $q->prepare();
    $stmt->execute();

  }


}


?>