<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */

  $path = ini_get("include_path");
  ini_set("include_path", sprintf("%s;%s", $path, dirname( __FILE__ ) . '/../phpdata'));

  $display = 1;
  $debug = 0;


  if ($debug)
    error_reporting(E_ALL);
  else
    error_reporting(0);

  // PEAR Authentification module
  require_once "Auth.php";

  // Smarty Template Engine
  require_once "smarty/Smarty.class.php";

  // eZComponents module autoloader
  require_once "ezc/Base/base.php"; // dependent on installation method, see below
  function __autoload( $className )
  {
      ezcBase::autoload( $className );
  }

  // Iinitialize configuration handler
  $cfg = ezcConfigurationManager::getInstance();
  $cfg->init( 'ezcConfigurationIniReader', dirname( __FILE__ ) . '/../phpdata' );

  // read database configuration from config.ini file and store in $db_settings
  $db_settings = $cfg->getSettings( 'config', 'Database', array( 'Type', 'Host', 'User', 'Pass', 'Base' ) );

  // initialize database connection and set $db instance as default
  $dsn = sprintf("%s://%s%s@%s/%s", $db_settings['Type'], $db_settings['User'], $db_settings['Password'], $db_settings['Host'], $db_settings['Base']);
  $db = ezcDbFactory::create( $dsn );
  ezcDbInstance::set( $db );


  // Include the classes into our application
  foreach(glob('../phpdata/libs/*.class.php') as $class){
    require_once($class);
  }

  // Setup Smarty Template Engine Envirnoment
  $smarty = new Smarty();

  $smarty->template_dir = dirname( __FILE__ ) . '/../smarty/templates/';
  $smarty->compile_dir = dirname( __FILE__ ) . '/../smarty/templates_c/';

  if ($debug)
    $smarty->debugging = true;
  else
    $smarty->debugging = false;


  switch($_GET['section']){
    case "browse":
      include "modules/browse/index.php";
      break;
    case "search":
      include "modules/search/index.php";
      break;
    default:
      include "modules/browse/index.php";
  } // switch


  $queue = Queue::getAll();
  $smarty->assign("QUEUE", $queue);

  // assign the $body_template to the base layout
  $smarty->assign("BODY_TEMPLATE", $body_template);

  // display the default template
  if ($display) {
    $smarty->display('base.tpl');
  }

?>