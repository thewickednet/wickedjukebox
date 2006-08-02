<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */

  set_time_limit(180);
  $finfo = finfo_open(FILEINFO_MIME);


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