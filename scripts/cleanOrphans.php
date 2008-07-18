<?php


//////////////////////////////////
// Zend Framework includes

require_once 'Zend/Db.php';
require_once 'Zend/Form.php';
require_once 'Zend/Form/Element.php';
require_once 'Zend/Registry.php';
require_once 'Zend/Cache.php';
require_once 'Zend/Config/Ini.php';

require_once('../phpdata/classes/Artist.class.php');
require_once('../phpdata/classes/Album.class.php');
require_once('../phpdata/classes/Song.class.php');

//////////////////////////////////
// CONFIG
//
// Retrieve the configuration data from the INI file

$db_config = new Zend_Config_Ini('../config.ini', 'database');


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


$select = $db->select()
             ->from(array('s' => 'song'));

$stmt = $select->query();
$result = $stmt->fetchAll();

$missing_files = array();

foreach ($result as $item) {
    if (!file_exists($item['localpath'])) {
        array_push($missing_files, $item);
    }
}

printf("%d orphans found.\n", count($missing_files));

foreach ($missing_files as $missing_file) {
    Song::delete($missing_file['id']);
}

$query = "DELETE FROM album WHERE id NOT IN (SELECT DISTINCT album_id FROM song)";

$db->query($query);

$cache->clean(Zend_Cache::CLEANING_MODE_ALL);

?>