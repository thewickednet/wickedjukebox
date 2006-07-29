<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */


  require_once 'Pager/Pager.php';

  switch($_GET['module']){
    case "artist":
      include "modules/browse/artists.php";
      break;
    case "albums":
      include "modules/browse/albums.php";
      break;
    case "genres":
      include "modules/browse/genres.php";
      break;
    default:
      include "modules/browse/artists.php";
  } // switch


?>