<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */



  switch($_GET['module']){
    case "artist":
      include "modules/browse/artists.php";
      break;
    case "albums":
      include "modules/browse/albums.php";
      break;
    default:
      include "modules/browse/artists.php";
  } // switch


?>