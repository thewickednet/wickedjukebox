<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */



  switch($_GET['module']){
    case "artist":
      include "modules/details/artist.php";
      break;
    case "song":
      include "modules/details/song.php";
      break;
    case "album":
      include "modules/details/album.php";
      break;
    default:
      header("Location: index.php");
  } // switch


?>