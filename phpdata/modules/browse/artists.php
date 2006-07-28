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
    case "cover":

      $cover = Artist::hasCover($_GET['param']);

      if (!empty($cover))
        Artist::showCover($cover);
      else
        echo "no cover found";
      exit();

      break;
    case "byid":

      $artist = Artist::getById($_GET['param']);

      $results = Artist::getSongs($_GET['param']);

      $smarty->assign("COVER", Artist::hasCover($_GET['param']));
      $smarty->assign("ARTIST", $artist);
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