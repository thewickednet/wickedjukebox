<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */

class Song {

  function getById($id = 0){

    $db = ezcDbInstance::get();

    $stmt = $db->prepare("SELECT * FROM songs, artists WHERE songs.artist_id = artists.artist_id AND songs.song_id = ? LIMIT 1");
    $stmt->execute(array("$id"));

    $result = $stmt->fetchAll();

    return $result[0];
  }

  function countDownload($id) {
    $db = ezcDbInstance::get();

    $q = $db->createUpdateQuery();
    $e = $q->expr;
    $q->update( 'songs' )
      ->set( 'downloaded', 'downloaded+1' )
      ->where( $e->eq( 'song_id', $q->bindValue( $id ) ) );
    $stmt = $q->prepare();
    $stmt->execute();

  }

  function countPlay($id) {
    $db = ezcDbInstance::get();

    $q = $db->createUpdateQuery();
    $e = $q->expr;
    $q->update( 'songs' )
      ->set( 'played', 'played+1' )
      ->where( $e->eq( 'song_id', $q->bindValue( $id ) ) );
    $stmt = $q->prepare();
    $stmt->execute();

  }

  function countSkip($id) {
    $db = ezcDbInstance::get();

    $q = $db->createUpdateQuery();
    $e = $q->expr;
    $q->update( 'songs' )
      ->set( 'skipped', 'skipped+1' )
      ->where( $e->eq( 'song_id', $q->bindValue( $id ) ) );
    $stmt = $q->prepare();
    $stmt->execute();

  }


  function getPlays(){
    $db = ezcDbInstance::get();

    $q = $db->createSelectQuery();
    $e = $q->expr;
    $q->select( '*' )
      ->from( 'songs' )
      ->orderBy('played', ezcQuerySelect::DESC)
      ->limit( '10' );

    $stmt = $q->prepare();
    $stmt->execute();

    $rows = $stmt->fetchAll();
    return $rows;
  }

  function getDownloads(){
    $db = ezcDbInstance::get();

    $q = $db->createSelectQuery();
    $e = $q->expr;
    $q->select( '*' )
      ->from( 'songs' )
      ->orderBy('downloaded', ezcQuerySelect::DESC)
      ->limit( '10' );

    $stmt = $q->prepare();
    $stmt->execute();

    $rows = $stmt->fetchAll();
    return $rows;
  }

  function getSkips(){
    $db = ezcDbInstance::get();

    $q = $db->createSelectQuery();
    $e = $q->expr;
    $q->select( '*' )
      ->from( 'songs' )
      ->orderBy('skipped', ezcQuerySelect::DESC)
      ->limit( '10' );

    $stmt = $q->prepare();
    $stmt->execute();

    $rows = $stmt->fetchAll();
    return $rows;
  }

}

?>