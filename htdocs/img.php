<?php

error_reporting(0);

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

$category   = $_GET['category'];
$preset     = $_GET['preset'];
$id         = $_GET['id'];

$cover = "";

switch ($category) {
    case "song":
        $song = Song::get($id);
        $album_cover = Album::findCover($song['album_id']);
        $artist_cover = Artist::findCover($song['artist_id']);
        if (!empty($album_cover)) {
            $cover = $album_cover;
        } elseif (!empty($artist_cover)) {
            $cover = $artist_cover;
        }
    break;
    case "album":
        $album_cover = Album::findCover($id);
        if (!empty($album_cover))
            $cover = $album_cover;
    break;
    case "artist":
        $artist_cover = Artist::findCover($id);
        if (!empty($artist_cover))
            $cover = $artist_cover;
    break;
    
}

$cache_key = sprintf("coverart_%s_%s_%s", $category, $preset, $id);

if ($_GET['flush'] == '1')
	$cache->remove($cache_key);

//if(!$data = $cache->load($cache_key)) {
    
	$img = new Renderer($category, $preset, $cover);
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
//	$cache->save($data, $cache_key, 30);
//}

echo $data;

exit();

?>