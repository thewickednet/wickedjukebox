<?php

/**
 *
 * @version $Id$
 * @copyright 2006
 */

  error_reporting(0);

  function traverseDirTree($base, $fileFunc, $dirFunc = null, $afterDirFunc = null) {
    $subdirectories = opendir($base);
    while (($subdirectory = readdir($subdirectories)) !== false) {
        $path = $base . $subdirectory;
        if (is_file($path)) {
            if ($fileFunc !== null) $fileFunc($path);
        } else {
            if ($dirFunc !== null) $dirFunc($path);
            if (($subdirectory != '.') && ($subdirectory != '..')) {
                traverseDirTree($path . '/', $fileFunc, $dirFunc, $afterDirFunc);
            }
            if ($afterDirFunc !== null) $afterDirFunc($path);
        }
    }
  }



  function importSong($file){
    $finfo = finfo_open(FILEINFO_MIME);
    if (count(Song::getByLocalPath($file)) > 0) {
      echo "file exists already in database. skipping.";
    } else {
      $getID3 = new getID3;
      $tags = array();

      if (finfo_file($finfo, $file) == "audio/mpeg") {
        $tag = $getID3->analyze($file);
        print_r($tag);

        if (isset($tag['tags']['id3v2']))
          $tags = $tag['tags']['id3v2'];
        elseif (isset($tag['tags']['id3v1']))
          $tags = $tag['tags']['id3v1'];
        else
          echo "no tags found in mp3 file: $file\n";


        if (count($tags) > 0) {

          $data = array(
                        'artist'    => rtrim($tags['artist'][0]),
                        'album'     => rtrim($tags['album'][0]),
                        'year'      => $tags['year'][0],
                        'track_no'  => $tags['track'][0],
                        'title'     => rtrim($tags['title'][0]),
                        'filesize'  => $tag['filesize'],
                        'localpath' => $file,
                        'genre'     => rtrim($tags['genre'][0]),
                        'checksum'  => md5_file($file)
                       );

          $audio = $tag['audio'];

          if (strtolower($audio['bitrate_mode']) == 'cbr')
            $data['bitrate'] = $audio['bitrate'] / 1000 . "kbps";
          else
            $data['bitrate'] = "VBR";

          $data['duration'] = secondsToMinutes($tag['playtime_seconds']);

          $data['genre_id'] = Genre::getByName(rtrim($tags['genre'][0]));

          print_r($data);


          $artist = Artist::getByName($data['artist']);

          if (count($artist) == 0) {
            $artist = Artist::add($data['artist']);
            $artist = Artist::getById($artist);
          }

          if (!empty($data['album'])) {
            $album = Album::getByTitle($data['album']);
    
            $album_data = array(
                                'title' => $data['album'],
                                'artist_id' => $artist['artist_id']
                              );
    
            if (count($album) == 0) {
              $album = Album::add($album_data);
              $album = Album::getById($album);
            }
  
            $data['album_id'] = $album['album_id'];
          } else {
            $data['album_id'] = null;
          }

          $data['artist_id'] = $artist['artist_id'];

          Song::add($data);

          if (Album::countArtists($data['album_id']) > 1) 
            Album::setType($data['album_id'], "various");

        }

      }
    }

  }


  function secondsToMinutes($seconds) {
    $seconds = round($seconds);
    $minutes = floor($seconds / 60);
    $seconds = $seconds - $minutes * 60;
    return sprintf("00:%02d:%02d", $minutes, $seconds);

  }

?>
