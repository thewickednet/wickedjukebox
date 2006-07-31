<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */

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

  $cache_settings = $cfg->getSettings( 'config', 'Cache', array( 'DirectoryShort', 'DirectoryLong', 'Type', 'TTLShort', 'TTLLong' ) );

  // initialize database connection and set $db instance as default
  $dsn = sprintf("%s://%s:%s@%s/%s", $db_settings['Type'], $db_settings['User'], $db_settings['Pass'], $db_settings['Host'], $db_settings['Base']);
  $db = ezcDbFactory::create( $dsn );
  ezcDbInstance::set( $db );

  ezcCacheManager::createCache( 'short', dirname( __FILE__ ) . '/../'. $cache_settings['DirectoryShort'], $cache_settings['Type'], array('ttl' => $cache_settings['TTLShort']) );
  ezcCacheManager::createCache( 'long', dirname( __FILE__ ) . '/../'. $cache_settings['DirectoryLong'], $cache_settings['Type'], array('ttl' => $cache_settings['TTLLong']) );

  // Include the classes into our application
  foreach(glob('../phpdata/libs/*.class.php') as $class){
    require_once($class);
  }

  require_once "libs/misc.php";

?>