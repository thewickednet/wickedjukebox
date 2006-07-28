<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */


  $alpha = Album::getAlphaIndex();
  $smarty->assign("ALPHA_INDEX", $alpha);

  switch($_GET['mode']){
    case "cover":

      $cover = Album::hasCover($_GET['param']);

      if (!empty($cover))
        Album::showCover($cover);
      else
        echo "no cover found";
      exit();

      break;
    case "byid":

      $album = Album::getById($_GET['param']);

      $results = Album::getSongs($_GET['param']);

      $smarty->assign("COVER", Album::hasCover($_GET['param']));
      $smarty->assign("ARTIST", Artist::getById($album['artist_id']));
      $smarty->assign("ALBUM", $album);
      $smarty->assign("SONGS", $results);

      $body_template = 'browse/album_songs.tpl';

      break;
    default:
    case "byalpha":

      if (!empty($_GET['param']))
        $alpha = $_GET['param'];
      else
        $alpha = $alpha[0]['alpha'];


      $results = Album::getByAlpha($alpha);

      $smarty->assign("ALBUMS", $results);

      $body_template = 'browse/albums.tpl';

      break;
  } // switch


?>