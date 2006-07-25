<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */



  switch($_GET['module']){
    case "artists":
      include "modules/browse/artists.php";
      break;
    case "genres":
      include "modules/browse/genres.php";
      break;
    case "latest":
      include "modules/browse/latest.php";
      break;
    case "albums":
      include "modules/browse/albums.php";
      break;
    default:
      include "modules/browse/artists.php";
  } // switch


?>