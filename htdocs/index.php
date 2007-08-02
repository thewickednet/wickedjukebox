<?php

header('Content-Type: text/html; charset=utf-8');
session_start();

require_once('../phpdata/classes/Auth.class.php');
require_once('../phpdata/classes/Core.class.php');
require_once('../phpdata/classes/Artist.class.php');
require_once('../phpdata/classes/Album.class.php');
require_once('../phpdata/classes/Genre.class.php');
require_once('../phpdata/classes/Queue.class.php');
require_once('../phpdata/classes/Channel.class.php');
require_once('../phpdata/classes/User.class.php');

//////////////////////////////////
// CONFIG
//
// Retrieve the configuration data from the INI file

require_once 'Zend/Config/Ini.php';
$db_config = new Zend_Config_Ini('../config.ini', 'database');
$demon_config = new Zend_Config_Ini('../config.ini', 'demon');


//////////////////////////////////
// DATABASE
// 
// initiate the Database connection

require_once 'Zend/Db.php';

$params = array (
                 'dbname'   => $db_config->Base,
                 'host'     => $db_config->Host,
                 'username' => $db_config->User,
                 'password' => $db_config->Pass
                 );

$db = Zend_Db::factory('Pdo_Mysql', $params);
unset($db_config);


//////////////////////////////////
// CORE
//
// Get the Jukebox Core. Mainly used as a container

$core = new Core($demon_config);
unset($demon_config);


require_once 'Zend/Registry.php';

$registry = new Zend_Registry(array('database' => $db, 'core' => $core));

Zend_Registry::setInstance($registry);


//////////////////////////////////
// TEMPLATES
//
// Setup the Smarty Template engine

require_once('Smarty.class.php');

$smarty = new Smarty();

$smarty->template_dir = '../templates/';
$smarty->compile_dir  = '../httpd_data/templates/';

$core->template = "base.tpl";

$smarty->assign("USERINFO", $core->userinfo);


if (Auth::isAuthed()) {
    $core->user_id = Auth::getAuth();
    $core->userdata = User::getUser($core->user_id);
    $core->permissions = User::getPermissions($core->userdata['group_id']);
}


/////////////////////////////////////////////////////////////
// AUTO-PREPEND ENDS HERE 
/////////////////////////////////////////////////////////////


switch ($_GET['module']) {
    case "auth":
        include "../phpdata/modules/auth/index.php";
    break;
    case "channel":
        include "../phpdata/modules/channel/index.php";
    break;
    case "album":
        include "../phpdata/modules/album/index.php";
    break;
    case "genre":
        include "../phpdata/modules/genre/index.php";
    break;
    case "artist":
    default:
        include "../phpdata/modules/artist/index.php";
    break;
}


/////////////////////////////////////////////////////////////
// AUTO-PREPEND STARTS HERE 
/////////////////////////////////////////////////////////////
$smarty->assign("CORE", $core);
$smarty->assign("QUEUE", Queue::getCurrent());

$smarty->assign("BODY_TEMPLATE", $body_template);

$smarty->assign("CHANNEL_LIST", $core->reIndex(Channel::getList(), 'id', 'name'));


if ($core->display)
    $smarty->display($core->template);


?>
