<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */


class Album {

  function getAlphaIndex(){

    $db = ezcDbInstance::get();

    $res = $db->query("SELECT DISTINCT SUBSTRING(title,1,1) AS alpha FROM albums ORDER BY alpha");
    return $res->fetchAll();
  }

  function getByAlpha($alpha = "A"){

    $db = ezcDbInstance::get();

    $stmt = $db->prepare("SELECT * FROM albums WHERE title LIKE ? ORDER BY title");
    $stmt->execute(array("$alpha%"));

    return $stmt->fetchAll();
  }

  function getById($id = ""){

    $db = ezcDbInstance::get();

    $stmt = $db->prepare("SELECT * FROM albums WHERE album_id = ? LIMIT 1");
    $stmt->execute(array("$id"));
    $result = $stmt->fetchAll();

    return $result[0];
  }

  function countArtists($id = ""){

    $db = ezcDbInstance::get();

    $stmt = $db->prepare("SELECT COUNT(DISTINCT artist_id) AS artists FROM songs WHERE album_id = ?");
    $stmt->execute(array("$id"));
    $result = $stmt->fetchAll();

    return $result[0]['artists'];
  }

  function getSongs($id = 0){

    $db = ezcDbInstance::get();

    $results = array();

    $stmt = $db->prepare("SELECT *, songs.title AS song, albums.title AS album, SEC_TO_TIME(duration) AS duration FROM songs, albums WHERE songs.album_id = albums.album_id AND albums.album_id = ? ORDER BY albums.title, track_no, song");
    $stmt->execute(array("$id"));
    return $stmt->fetchAll();
  }

  function setType($id = 0, $type = "album") {
    $db = ezcDbInstance::get();

    $cookie = md5(time());

    $q = $db->createUpdateQuery();
    $e = $q->expr;
    $q->update( 'albums' )
      ->set( 'type', $q->bindValue( $type ) )
      ->where( $e->eq( 'album_id', $q->bindValue( $id ) ) );

    if ($type != "album")
      $q->set('artist_id', null);

    $stmt = $q->prepare();
    $stmt->execute();

  }

  function countPlay($id) {
    $db = ezcDbInstance::get();

    $q = $db->createUpdateQuery();
    $e = $q->expr;
    $q->update( 'albums' )
      ->set( 'played', 'played+1' )
      ->where( $e->eq( 'album_id', $q->bindValue( $id ) ) );
    $stmt = $q->prepare();
    $stmt->execute();

  }

  function countDownload($id) {
    $db = ezcDbInstance::get();

    $q = $db->createUpdateQuery();
    $e = $q->expr;
    $q->update( 'albums' )
      ->set( 'downloaded', 'downloaded+1' )
      ->where( $e->eq( 'album_id', $q->bindValue( $id ) ) );
    $stmt = $q->prepare();
    $stmt->execute();

  }


    function getPlays(){
    $db = ezcDbInstance::get();

    $q = $db->createSelectQuery();
    $e = $q->expr;
    $q->select( '*' )
      ->from( 'albums' )
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
      ->from( 'albums' )
      ->orderBy('downloaded', ezcQuerySelect::DESC)
      ->limit( '10' );

    $stmt = $q->prepare();
    $stmt->execute();

    $rows = $stmt->fetchAll();
    return $rows;
  }


  function getByTitle($title){

    $db = ezcDbInstance::get();

    $stmt = $db->prepare("SELECT * FROM albums WHERE title = ? LIMIT 1");
    $stmt->execute(array("$title"));
    $result = $stmt->fetchAll();

    return $result[0];
  }


  function add($data){

    $db = ezcDbInstance::get();

    $q = $db->createInsertQuery();
    $q->insertInto( 'albums' )
      ->set( 'title', $q->bindValue( $data['title'] ) )
      ->set( 'artist_id', $q->bindValue( $data['artist_id'] ) )
      ->set( 'added', $q->bindValue(  strftime("%Y-%m-%d %H:%M:%S") ) );
    $stmt = $q->prepare();
    $stmt->execute();

    return $db->lastInsertId();

  }

  function hasCover($id = 0){

    $result = "";

    $filemasks = array('folder.jpg', 'Folder.jpg', 'cover.jpg');

    $songs = self::getSongs($id);
    foreach($songs as $song) {
      foreach($filemasks as $filemask){
        $check = dirname($song['localpath']) . '/' . $filemask;
        if (file_exists($check))
          return $check;
      }

    }

    return "";

  }

  function showCover($original){

    $w_max = 200;
    $h_max = 200;

    $src_size = getimagesize($original);

    $w_orig = $src_size[0];
    $h_orig = $src_size[1];

    $proportion = $src_size[0] / $src_size[1];
    $w_potentiel = $h_max * $proportion;
    $h_potentiel = $w_max / $proportion;
    if ($w_potentiel <= $w_max) {
      $format_final_w = $w_potentiel;
      $format_final_h = $h_max;
    } elseif ($h_potentiel <= $h_max) {
      $format_final_w = $w_max;
      $format_final_h = $h_potentiel;
    }

    $image_p = imagecreatetruecolor($format_final_w, $format_final_h);
    $image = imagecreatefromjpeg($original);
    imagecopyresampled($image_p, $image, 0, 0, 0, 0, $format_final_w, $format_final_h, $w_orig, $h_orig);
    header("Content-type: image/jpeg");
    imagejpeg($image_p, "", 80);
    exit();
  }

  function getTotalCount(){

    $db = ezcDbInstance::get();

    $stmt = $db->prepare("SELECT COUNT(*) FROM albums LIMIT 1");
    $stmt->execute(array());
    $result = $stmt->fetchAll();

    return $result[0];
  }


}



?>