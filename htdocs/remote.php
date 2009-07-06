<?php

header('Content-Type: text/html; charset=utf-8');
session_start();

//////////////////////////////////
// Zend Framework includes

require_once 'Zend/Db.php';
require_once 'Zend/Registry.php';
require_once 'Zend/Cache.php';
require_once 'Zend/Config/Ini.php';


//////////////////////////////////
// Local includes

require_once('../phpdata/classes/Auth.class.php');
require_once('../phpdata/classes/Core.class.php');
require_once('../phpdata/classes/Backend.class.php');
require_once('../phpdata/classes/BackendDB.class.php');
require_once('../phpdata/classes/Artist.class.php');
require_once('../phpdata/classes/Album.class.php');
require_once('../phpdata/classes/Song.class.php');
require_once('../phpdata/classes/Genre.class.php');
require_once('../phpdata/classes/Queue.class.php');
require_once('../phpdata/classes/Search.class.php');
require_once('../phpdata/classes/Channel.class.php');
require_once('../phpdata/classes/User.class.php');
require_once('../phpdata/classes/Icecast.class.php');
require_once('../phpdata/classes/Shoutbox.class.php');
require_once('../phpdata/classes/Settings.class.php');

//////////////////////////////////
// CONFIG
//
// Retrieve the configuration data from the INI file

$xml_config = new Zend_Config_Ini('../config.ini', 'xmlrpc');
$db_config = new Zend_Config_Ini('../config.ini', 'database');
$demon_config = new Zend_Config_Ini('../config.ini', 'demon');


//////////////////////////////////
// DATABASE
// 
// initiate the Database connection


$params = array (
                 'dbname'   => $db_config->Base,
                 'host'     => $db_config->Host,
                 'username' => $db_config->User,
                 'password' => $db_config->Pass
                 );

$db = Zend_Db::factory('Pdo_Mysql', $params);
unset($db_config);

$registry = new Zend_Registry(array('database' => $db));

Zend_Registry::setInstance($registry);

require_once 'Zend/Log.php';
require_once 'Zend/Log/Writer/Db.php';

$columnMapping = array('priority' => 'priority', 'message' => 'message');

$writer = new Zend_Log_Writer_Db($db, 'log', $columnMapping);

$logger = new Zend_Log($writer);

$registry->set('logger', $logger);

require_once 'Zend/XmlRpc/Client.php';

$xmlrpc = new Zend_XmlRpc_Client(sprintf("http://localhost:%d/RPC2", $xml_config->port));

$registry->set('xmlrpc', $xmlrpc);

//////////////////////////////////
// CORE
//
// Get the Jukebox Core. Mainly used as a container

$core = new Core($demon_config);
unset($demon_config);

$registry->set('core', $core);

$cacheFrontendOptions = array(
   'lifetime' => 7200, // cache lifetime of 2 hours
   'automatic_serialization' => true
);
$cache = Zend_Cache::factory('Core', 'Memcached', $cacheFrontendOptions);

$registry->set('cache', $cache);


//////////////////////////////////
// TEMPLATES
//
// Setup the Smarty Template engine

require_once('Smarty.class.php');

$smarty = new Smarty();

$smarty->template_dir = '../templates/_json/';
$smarty->compile_dir  = '../httpd_data/templates/json/';

$core->template = "base.tpl";

$smarty->register_modifier('bytesToHumanReadable', array('core','bytesToHumanReadable'));
$smarty->register_function('highLight', array('core','highLight'));


// TODO temporary set to exhuma.twn until auth implemented
$core->user_id = 1;
$core->userdata = User::getUser($core->user_id);
$core->permissions = User::getPermissions($core->userdata['group_id']);


/////////////////////////////////////////////////////////////
// AUTO-PREPEND ENDS HERE
/////////////////////////////////////////////////////////////

switch ($_GET['module']) {
    case "random_picker":
        include "../phpdata/json/random_picker.php";
    break;
    case "get_current":
        include "../phpdata/json/get_current.php";
    break;
    case "queue":
        include "../phpdata/json/queue/index.php";
    break;
}

/////////////////////////////////////////////////////////////
// AUTO-APPEND STARTS HERE
/////////////////////////////////////////////////////////////

$icecast = new Icecast();

$smarty->assign("ICECAST", $icecast->getData("localhost", 8001, "admin", "matourenstepp"));

$smarty->assign("CORE", $core);
$player_status = BackendDB::getCurrentSong($core->channel_id);

$smarty->display($core->template);

?>