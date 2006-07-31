<?php

/**
 *
 * @version $Id$
 * @copyright 2006
 */

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
      if (finfo_file($finfo, $file) == "audio/mpeg") {
        $tag = id3_get_tag($file);
        print_r($tag);
        $artist = Artist::getByName($tag['artist']);

        $album = Album::getByName($tag['album']);

        if (count($artist) == 0) {
          $artist = Artist::add($tag['artist']);
          $artist = Artist::getById($artist);
        }

      }
    }

  }

?>