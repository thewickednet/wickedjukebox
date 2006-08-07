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

    $stmt = $db->prepare("SELECT *, SEC_TO_TIME(duration) AS duration FROM songs, artists WHERE songs.artist_id = artists.artist_id AND songs.song_id = ? LIMIT 1");
    $stmt->execute(array("$id"));

    $result = $stmt->fetchAll();

    return $result[0];
  }

  function getByTitle($title){

    $db = ezcDbInstance::get();

    $stmt = $db->prepare("SELECT *, SEC_TO_TIME(duration) AS duration FROM songs WHERE title = ? LIMIT 1");
    $stmt->execute(array("$title"));
    $result = $stmt->fetchAll();

    return $result[0];
  }

  function getByLocalPath($filename){

    $db = ezcDbInstance::get();

    $stmt = $db->prepare("SELECT *, SEC_TO_TIME(duration) AS duration FROM songs WHERE localpath = ? LIMIT 1");
    $stmt->execute(array("$filename"));
    $result = $stmt->fetchAll();

    return $result[0];
  }

  function add($data){

    $db = ezcDbInstance::get();

    $q = $db->createInsertQuery();
    $q->insertInto( 'songs' )
      ->set( 'title', $q->bindValue( $data['title'] ) )
      ->set( 'artist_id', $q->bindValue( $data['artist_id'] ) )
      ->set( 'album_id', $q->bindValue( $data['album_id'] ) )
      ->set( 'genre_id', $q->bindValue( $data['genre_id'] ) )
      ->set( 'track_no', $q->bindValue( $data['track_no'] ) )
      ->set( 'year', $q->bindValue( $data['year'] ) )
      ->set( 'bitrate', $q->bindValue( $data['bitrate'] ) )
      ->set( 'duration', $q->bindValue( $data['duration'] ) )
      ->set( 'localpath', $q->bindValue( $data['localpath'] ) )
      ->set( 'filesize', $q->bindValue( $data['filesize'] ) )
      ->set( 'checksum', $q->bindValue( $data['checksum'] ) )
      ->set( 'added', $q->bindValue(  strftime("%Y-%m-%d %H:%M:%S") ) );
    $stmt = $q->prepare();
    $stmt->execute();

    $arr = $stmt->errorInfo();
    //print_r($arr);
    return $db->lastInsertId();

  }

  function getLatest($id = 0){

      $db = ezcDbInstance::get();

      $results = array();

      $stmt = $db->prepare("SELECT *, songs.title AS song, albums.title AS album, songs.added AS added_song, SEC_TO_TIME(duration) AS duration FROM songs, albums, artists WHERE artists.artist_id = songs.artist_id AND songs.album_id = albums.album_id ORDER BY songs.added DESC LIMIT 25");
      $stmt->execute(array());
      $results = $stmt->fetchAll();

    return $results;
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

  function getTotalCount(){

    $db = ezcDbInstance::get();

    $stmt = $db->prepare("SELECT COUNT(*) FROM songs LIMIT 1");
    $stmt->execute(array());
    $result = $stmt->fetchAll();

    return $result[0];
  }



}

?>
