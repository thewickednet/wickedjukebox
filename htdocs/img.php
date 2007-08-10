<?php

//////////////////////////////////
// Zend Framework includes

require_once 'Zend/Db.php';
require_once 'Zend/Registry.php';
require_once 'Zend/Cache.php';
require_once 'Zend/Config/Ini.php';


//////////////////////////////////
// Local includes

require_once('../phpdata/classes/Renderer.class.php');
require_once('../phpdata/classes/Artist.class.php');
require_once('../phpdata/classes/Album.class.php');
require_once('../phpdata/classes/Song.class.php');

//////////////////////////////////
// CONFIG
//
// Retrieve the configuration data from the INI file

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


$cacheFrontendOptions = array(
   'lifetime' => 7200, // cache lifetime of 2 hours
   'automatic_serialization' => true
);
$cache = Zend_Cache::factory('Core', 'Memcached', $cacheFrontendOptions);

$registry->set('cache', $cache);

error_reporting(0);
$category   = $_GET['category'];
$preset     = $_GET['preset'];
$id         = $_GET['id'];

$cache_key = sprintf("coverart-%s_%s-%s", $category, $preset, $id);

$memcache = $kernel->cache;
if ($_GET['flush'] == '1')
	$memcache->delete($cache_key);

if (!($data = $memcache->get($cache_key))) {
    
	$img = new Renderer($category, $preset, $filename, $folder);
	$img->true_color   = true;
	$img->out_file	   = $cache_key;
	
	ob_start();
	$img->render();
	$image = ob_get_contents();
	$size = ob_get_length();
	ob_end_clean();
	ob_start();
	header("Content-Transfer-Encoding: binary\n");
	header('Content-Length: '.$size);
    $header = ob_get_contents();
    ob_end_clean();
    $data = $header . $image;
	$data = base64_encode($data);
	$memcache->set($cache_key, $data, MEMCACHE_UNCOMPRESSED, $kernel->img_ttl);
    $kernel->log->info(sprintf("[RENDERER] - Category: %s - Filename: %s - Preset: %s - Folder: %s", $category, $filename, $preset, $folder));
}

$data = base64_decode($data);
echo $data;

exit();

?>