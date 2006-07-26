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

    $stmt = $db->prepare("SELECT * FROM queue, artists, users, songs WHERE queue.user_id = users.user_id AND artists.artist_id = songs.artist_id AND queue.song_id = songs.song_id AND channel_id = ? ORDER BY queue.added ASC, queue.position ASC");

    $stmt->execute(array("$channel"));

    return $stmt->fetchAll();

  }


  function getTotal($channel = 1){
    $db = ezcDbInstance::get();

    $stmt = $db->prepare("SELECT SEC_TO_TIME( SUM( TIME_TO_SEC( duration ) ) ) AS total_time FROM queue, songs WHERE queue.song_id = songs.song_id AND channel_id = ?");

    $stmt->execute(array("$channel"));

    return $stmt->fetch();

  }

  function add($song_id, $position = 0) {
    $db = ezcDbInstance::get();

    $q = $db->createInsertQuery();
    $q->insertInto( 'queue' )
      ->set( 'song_id', $q->bindValue( $song_id ) )
      ->set( 'channel_id', $q->bindValue( $this->channel_id ) )
      ->set( 'user_id', $q->bindValue( $this->user_id ) )
      ->set( 'position', $q->bindValue( $position ) )
      ->set( 'added', $q->bindValue(  strftime("%Y-%m-%d %H:%M:%S") ) );
    $stmt = $q->prepare();
    $stmt->execute();

  }

  function del($queue_id) {
    $db = ezcDbInstance::get();

    $q = $db->createDeleteQuery();
    $e = $q->expr;
    $q->deleteFrom( 'queue' )
      ->where( $e->eq( 'queue_id', $q->bindValue( $queue_id ) ) );

    $stmt = $q->prepare();
    $stmt->execute();

  }


}


?>