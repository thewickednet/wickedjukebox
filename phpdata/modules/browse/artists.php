<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */


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

      $pager_params = array(
          'mode'      => 'Sliding',
          'append'    => false,
          'urlVar'    => 'pagenum',
          'path'      => sprintf("http://%s/browse/artists/byid/%s/bypage/", $_SERVER["HTTP_HOST"], $_GET['param']),
          'fileName'  => '%d'.'/',  //Pager replaces "%d" with page number...
          'itemData'  => $results,
          'perPage'   => 25
      );

      $pager = & Pager::factory($pager_params);
      $data  = $pager->getPageData();
      $links = $pager->getLinks();

      $smarty->assign("LINKS", $links['all']);
      $smarty->assign("COVER", Artist::hasCover($_GET['param']));
      $smarty->assign("ARTIST", $artist);
      $smarty->assign("SONGS", $data);

      $body_template = 'browse/artist_songs.tpl';

      break;
    default:
    case "byalpha":

      if (!empty($_GET['param']))
        $alpha = $_GET['param'];
      else
        $alpha = "A";

      if ($alpha != 'various' && $alpha != 'ost' && $alpha != 'videogame') {
        $results = Artist::getByAlpha($alpha);
        $smarty->assign("ARTISTS", $results);

        $body_template = 'browse/artists.tpl';
      } else {
        $results = Artist::getByType($alpha);


        $pager_params = array(
            'mode'      => 'Sliding',
            'append'    => false,
            'urlVar'    => 'pagenum',
            'path'      => sprintf("http://%s/browse/artists/byid/%d/bypage/", $_SERVER["HTTP_HOST"], $_GET['param']),
            'fileName'  => '%d'.'/',  //Pager replaces "%d" with page number...
            'itemData'  => $results,
            'perPage'   => 25
        );

        $pager = & Pager::factory($pager_params);
        $data  = $pager->getPageData();
        $links = $pager->getLinks();



        switch($alpha){
          case "various":
            $artist = array('name' => 'Various Artists');
            break;
          case "ost":
            $artist = array('name' => 'Soundtracks');
            break;
          case "videogame":
            $artist = array('name' => 'Video Games');
            break;
        } // switch

        $smarty->assign("ARTIST", $artist);
        $smarty->assign("SONGS", $results);
        $smarty->assign("LINKS", $links['all']);

        $body_template = 'browse/artist_songs.tpl';
      }


      break;
  } // switch




?>
