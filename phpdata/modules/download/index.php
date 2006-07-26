<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */



  switch($_GET['module']){
    case "song":
      include "modules/download/song.php";
      break;
    case "album":
      include "modules/download/album.php";
      break;
    default:
      header("Location: index.php");
  } // switch


?>