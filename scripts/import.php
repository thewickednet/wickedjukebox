<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */


  $path = ini_get("include_path");
  ini_set("include_path", sprintf("%s:%s", $path, dirname( __FILE__ ) . '/../phpdata'));

  $debug = 0;

  if ($debug)
    error_reporting(E_ALL);
  else
    error_reporting(0);

  require_once "base.php";

  require_once "libs/getid3/getid3.php";

  $base_folder = Setting::get("folders");
  $base_folder = $base_folder['value'];

  if (file_exists($base_folder)) {
    echo "scanning folder: $base_folder\n";
    traverseDirTree($base_folder, "importSong");
  } else {
    echo "folder does not exist: $base_folder\n";
  }



?>
