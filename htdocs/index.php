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

$smarty->template_dir = '../templates/';
$smarty->compile_dir  = '../httpd_data/templates/';

$core->template = "base.tpl";

$smarty->register_modifier('bytesToHumanReadable', array('core','bytesToHumanReadable'));
$smarty->register_function('highLight', array('core','highLight'));

if (Auth::isAuthed()) {
    $core->user_id = Auth::getAuth();
    $core->userdata = User::getUser($core->user_id);
    $core->permissions = User::getPermissions($core->userdata['group_id']);
    User::giveProof();
}


/////////////////////////////////////////////////////////////
// AUTO-PREPEND ENDS HERE
/////////////////////////////////////////////////////////////


switch ($_GET['module']) {
    case "auth":
        include "../phpdata/modules/auth/index.php";
    break;
    case "authrefresh":
        include "../phpdata/modules/auth/refresh.php";
    break;
    case "channel":
        include "../phpdata/modules/channel/index.php";
    break;
    case "stats":
        include "../phpdata/modules/stats/index.php";
    break;
    case "backend":
        include "../phpdata/modules/backend/index.php";
    break;
    case "backenddb":
        include "../phpdata/modules/backenddb/index.php";
    break;
    case "queue":
        include "../phpdata/modules/queue/index.php";
    break;
    case "search":
        include "../phpdata/modules/search/index.php";
    break;
    case "album":
        include "../phpdata/modules/album/index.php";
    break;
    case "song":
        include "../phpdata/modules/song/index.php";
    break;
    case "genre":
        include "../phpdata/modules/genre/index.php";
    break;
    case "artist":
    default:
        include "../phpdata/modules/artist/index.php";
    break;
    case "player":
        include "../phpdata/modules/player/index.php";
    break;
    case "user":
        include "../phpdata/modules/user/index.php";
    break;
    case "shoutbox":
        include "../phpdata/modules/shoutbox/index.php";
    break;
}


/////////////////////////////////////////////////////////////
// AUTO-APPEND STARTS HERE
/////////////////////////////////////////////////////////////

$icecast = new Icecast();

$smarty->assign("ICECAST", $icecast->getData("localhost", 8001, "admin", "matourenstepp"));

$smarty->assign("CORE", $core);
$player_status = BackendDB::getCurrentSong(0);

if (Auth::isAuthed()) {
    $player_status['standing'] = User::getStanding($player_status['songinfo']['id']);
    $player_status['auth'] = 'yes';

    $smarty->assign("PLAYER_STATUS", $player_status);
    
    $smarty->assign("ALIVE_USERS", User::getAlive());
    
    $smarty->assign("QUEUE", Queue::getCurrent());
    $smarty->assign("QUEUE_TOTAL", Queue::getTotalTime());
    
    $smarty->assign("RANDOM_SONGS", Song::getRandom());
    
    $smarty->assign("CHANNEL_LIST", $core->reIndex(Channel::getList(), 'id', 'name'));

} else {
    $body_template = "notloggedin.tpl";
}


$smarty->assign("BODY_TEMPLATE", $body_template);

if ($core->display)
    $smarty->display($core->template);

?>