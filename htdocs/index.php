<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */

  session_start();

  $path = ini_get("include_path");
  ini_set("include_path", sprintf("%s:%s", $path, dirname( __FILE__ ) . '/../phpdata'));

  $temp_path = dirname( __FILE__ ) . '/../tmp';

  $base_template = 'base.tpl';
  $display = 1;
  $debug = 1;

  $genre_index = array();


  if ($debug)
    error_reporting(E_ALL);
  else
    error_reporting(0);

  // Smarty Template Engine
  require_once "smarty/Smarty.class.php";

  // Wicked Jukebox PHP base
  require_once "base.php";

  // Authentification module
  if (User::isAuthed()) {
    $userinfo = User::getByCookie($_SESSION['wjukebox_auth']);
    $permissions = User::getPermissions($userinfo['group_id']);
  } else{
    $userinfo = array();
    $permissions = array();
  }
  // Setup Smarty Template Engine Envirnoment
  $smarty = new Smarty();

  $smarty->template_dir = dirname( __FILE__ ) . '/../smarty/templates/';
  $smarty->compile_dir = dirname( __FILE__ ) . '/../smarty/templates_c/';

  $smarty->compile_check = true;
  $smarty->caching = false;

  if ($debug)
    $smarty->debugging = true;
  else
    $smarty->debugging = false;

  require_once "libs/smarty_functions.php";

  $genre_index = Genre::getAll();
  $smarty->assign("GENRE_INDEX", $genre_index);

  switch($_GET['section']){
    case "browse":
      include "modules/browse/index.php";
      break;
    case "search":
      include "modules/search/index.php";
      break;
    case "queue":
      include "modules/queue/index.php";
      break;
    case "details":
      include "modules/details/index.php";
      break;
    case "download":
      include "modules/download/index.php";
      break;
    case "stats":
      include "modules/stats/index.php";
      break;
    case "backend":
      include "modules/backend/index.php";
      break;
    case "login":
      include "modules/login/index.php";
      break;
    default:
      include "modules/browse/index.php";
  } // switch


  $smarty->assign("USERINFO", $userinfo);
  $smarty->assign("PERMISSIONS", $permissions);
  $smarty->assign("PLAYER_STATUS", Player::getStatus());
  $smarty->assign("QUEUE", Queue::getAll());
  $smarty->assign("QUEUE_TOTAL", Queue::getTotal());

  // assign the $body_template to the base layout
  $smarty->assign("BODY_TEMPLATE", $body_template);
  $smarty->assign("URL", $_SERVER['REQUEST_URI']);

  // display the default template
  if ($display) {
    $smarty->display($base_template);
  }

?>

