<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */

  $smarty->assign("SEARCH_PATTERN", $_GET['pattern']);
  $smarty->assign("SEARCH_MODE", $_GET['mode']);

  switch($_GET['mode']){
    case "artist":
      $results = Search::findArtist($_GET['pattern']);
      break;
    case "album":
      $results = Search::findAlbum($_GET['pattern']);
      break;
    case "song":
      $results = Search::findSong($_GET['pattern']);
      break;
    default:
    case "any":
      $results = Search::findAny($_GET['pattern']);
      break;
  } // switch


  $smarty->assign("RESULTS", $results);

  $body_template = 'search.tpl';

?>