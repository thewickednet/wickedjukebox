<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */


  $alpha = Artist::getAlphaIndex();
  $smarty->assign("ALPHA_INDEX", $alpha);

  switch($_GET['mode']){
    case "byid":

      $artist = Artist::getById($_GET['param']);

      $results = Artist::getSongs($_GET['param']);

      $smarty->assign("ARTIST", $artist[0]);
      $smarty->assign("SONGS", $results);

      $body_template = 'browse/artist_songs.tpl';

      break;
    default:
    case "byalpha":

      if (!empty($_GET['param']))
        $alpha = $_GET['param'];
      else
        $alpha = $alpha[0]['alpha'];


      $results = Artist::getByAlpha($alpha);

      $smarty->assign("ARTISTS", $results);

      $body_template = 'browse/artists.tpl';

      break;
  } // switch




?>