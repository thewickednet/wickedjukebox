<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */

  if ($permissions['admin'] != '1')
    die("waat get daat do dann? an schnell raus elei! soss soen ech denger mamm et!");

  require_once 'Pager/Pager.php';

  switch($_GET['module']){
    case "artists":
      include "modules/admin/artists.php";
      break;
    case "albums":
      include "modules/admin/albums.php";
      break;
    case "songs":
      include "modules/admin/songs.php";
      break;
    case "users":
      include "modules/admin/users.php";
      break;
    case "groups":
      include "modules/admin/groups.php";
      break;
    case "settings":
      include "modules/admin/settings.php";
      break;
    default:
      include "modules/admin/welcome.php";
  } // switch


?>
