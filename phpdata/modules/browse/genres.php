<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */


  $genres = Genre::getAvailable();

  switch($_GET['mode']){
    case "byid":

      $genre = Genre::getById($_GET['param']);

      $results = Genre::getSongs($_GET['param']);

      $pager_params = array(
          'mode'      => 'Sliding',
          'append'    => false,
          'urlVar'    => 'pagenum',
          'path'      => sprintf("http://%s/browse/genres/byid/%d/bypage/", $_SERVER["HTTP_HOST"], $_GET['param']),
          'fileName'  => '%d'.'/',  //Pager replaces "%d" with page number...
          'itemData'  => $results,
          'perPage'   => 25
      );

      $pager = & Pager::factory($pager_params);
      $data  = $pager->getPageData();
      $links = $pager->getLinks();



      $smarty->assign("LINKS", $links['all']);
      $smarty->assign("GENRE", $genre);
      $smarty->assign("SONGS", $data);

      $body_template = 'browse/genre_songs.tpl';

      break;
    default:
    case "byalpha":

      $smarty->assign("GENRES", $genres);

      $body_template = 'browse/genres.tpl';

      break;
  } // switch




?>