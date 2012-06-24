<?php

class Bootstrap extends Zend_Application_Bootstrap_Bootstrap
{
    /*
     * Autoload stuff from the default module (which is not in a `modules` subfolder in this project)
     * (Api_, Form_, Model_, Model_DbTable, Plugin_)
     * */
    protected function _initAutoloader()
    {
        require_once APPLICATION_ROOT . '/vendor/Doctrine/Common/ClassLoader.php';

        $autoloader = \Zend_Loader_Autoloader::getInstance();

        $bisnaAutoloader = new \Doctrine\Common\ClassLoader('Bisna');
        $autoloader->pushAutoloader(array(
            $bisnaAutoloader, 'loadClass'
        ), 'Bisna');

        $appAutoloader = new \Doctrine\Common\ClassLoader('WJB');
        $autoloader->pushAutoloader(array(
            $appAutoloader, 'loadClass'
        ), 'WJB');
    }


    /*     *
     * Autoload stuff from the default module (which is not in a `modules` subfolder in this project)
     * (Api_, Form_, Model_, Model_DbTable, Plugin_)
     * */
    protected function _initAutoload() {
        $moduleLoader = new Zend_Application_Module_Autoloader(array(
            'namespace' => '',
            'basePath' => APPLICATION_ROOT));

        $moduleLoader->addResourceType('Model', 'models', 'Model');

        return $moduleLoader;
    }

    protected function _initDoctitle()
    {
        $view = new Zend_View($this->getOptions());
        $view->headTitle('Wicked Jukebox');
    }

    protected function _initCache() {

        $options = $this->getOption('memcache');
        $cacheBackendOptions = array(
            'servers' => array('host' => $options['host'], 'port' => $options['port'])
        );

        $cacheFrontendOptions = array(
            'lifetime' => 7200, // cache lifetime of 2 hours
            'automatic_serialization' => true
        );

        $memcache = Zend_Cache::factory('Core', 'Memcached', $cacheFrontendOptions, $cacheBackendOptions);
        $front = Zend_Controller_Front::getInstance();

        $front->setParam('cache', $memcache);
        Zend_Registry::set('cache', $memcache);

    }


    protected function _initLog()
    {
        $this->bootstrap('frontController');
        $logger = new \Zend_Log();
        Zend_Registry::set('log', $logger);
        try
        {
            $file_writer = new Zend_Log_Writer_Stream(APPLICATION_ROOT . '/logs/app.log');
            $logger->addWriter($file_writer);
        }
        catch (Exception $e)
        {
            $null_writer = new Zend_Log_Writer_Null();
            $logger->addWriter($null_writer);
        }
    }

    protected function _initRequest()
    {
        $this->bootstrap('frontController');
        $front = Zend_Controller_Front::getInstance();
        $request = $front->getRequest();
        if ($front->getRequest() === null) {
            $request = new Zend_Controller_Request_Http();
            $front->setRequest($request);
        }
        return $request;
    }

    protected function _initRestRoute()
    {
        $this->bootstrap('frontController');
        $frontController = Zend_Controller_Front::getInstance();
        $restRoute = new Zend_Rest_Route($frontController, array(), array('rest'));
        $frontController->getRouter()->addRoute('rest', $restRoute);
    }

    protected function _initImagesRoute()
    {
        $this->bootstrap('frontController');
        $frontController = Zend_Controller_Front::getInstance();
        $route = new Zend_Controller_Router_Route(
            'images/:category/:preset/:filename',
            array('controller' => 'images', 'action' => 'render')
        );
        $frontController->getRouter()->addRoute('images', $route);
    }

    protected static function _initAuth()
    {
        $auth = Zend_Auth::getInstance();
        $front = Zend_Controller_Front::getInstance();
        $front->registerPlugin(
            new WJB_Controller_Plugin_Auth($auth), 1
        );

    }

}

