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
    case "byid":

      $album = Album::getById($_GET['param']);

      $results = Album::getSongs($_GET['param']);

      $smarty->assign("ARTIST", Artist::getById($album[0]['artist_id']));
      $smarty->assign("ALBUM", $album[0]);
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