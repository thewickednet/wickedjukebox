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

    $stmt = $db->prepare("SELECT * FROM albums WHERE album_id = ?");
    $stmt->execute(array("$id"));

    return $stmt->fetchAll();
  }

  function getSongs($id = 0){

    $db = ezcDbInstance::get();

    $results = array();

    $stmt = $db->prepare("SELECT *, songs.title AS song, albums.title AS album FROM songs, albums WHERE songs.album_id = albums.album_id AND albums.album_id = ? ORDER BY albums.title, track_no, song");
    $stmt->execute(array("$id"));
    return $stmt->fetchAll();
  }

  function hasCover($id = 0){

    $result = "";

    $songs = self::getSongs($id);
    foreach($songs as $song) {

      $check = dirname($song['localpath']) . '/folder.jpg';
      if (file_exists($check)) {
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



  function download($id = 0){

    // Archive Creation for Album Downloads
    require_once "Archive/Zip.php";

    $songs = Album::getSongs($id);

    $filename = sprintf("%s - %s.zip");
    $filename = str_replace(" ", "_", $filename);
    $files = array();


    foreach($songs as $song){
      array_push($files, $song['localpath']);
    }

    $zipfile = New Archive_Zip($filename);

    $zipfile->create($files);
    exit();

/*
    $filename = basename($song['localpath']);
    $extension = split(".", $filename);
    $extension = $extension[count($extension)-1];

    $filename = sprintf("%s - %s.%s", $song['name'], $song['name'], $extension );
    $filename = str_replace(" ", "_", $filename);


    $mime = mime_content_type($song['localpath']);
    header('Content-type: ' . $mime);
    header("Content-length: ".filesize($song['localpath']));
    header('Content-Disposition: attachment; filename="'.$filename.'"');
    $fp = fopen($song['localpath'], "r");
    fpassthru($fp);
    fclose($fp);
    exit();
*/
  }



}



?>