<?php

header('Content-Type: text/html; charset=utf-8');

//////////////////////////////////
// CORE
//
// Get the Jukebox Core. Mainly used as a container

require_once('classes/Core.class.php');

$core = Core::instance();

//////////////////////////////////
// CONFIG
//
// Retrieve the configuration data from the INI file

require_once 'Zend/Config/Ini.php';
$db_config = new Zend_Config_Ini('../config.ini', 'Database');



//////////////////////////////////
// DATABASE
// 
// initiate the Database connection

require_once 'Zend/Db.php';

$params = array ('dbname' => '../' . $db_config->File);

$db = Zend_Db::factory('Pdo_Sqlite', $params);


//////////////////////////////////
// TEMPLATES
//
// Setup the Smarty Template engine

require_once('Smarty.class.php');

$smarty = new Smarty();

$smarty->template_dir = '../templates/';
$smarty->compile_dir  = '../httpd_data/templates/';

$core->template = "base.tpl";






?>
