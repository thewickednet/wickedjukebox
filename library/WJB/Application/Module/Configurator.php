<?php

class WJB_Application_Module_Configurator
{

    public function __construct(Zend_Config $config)
    {
        $front = Zend_Controller_Front::getInstance();
        $this->_bootstrap = $front->getParam('bootstrap');
        $this->_config = $config;
    }

    public function run()
    {

        $resources = $this->_config->resources;

        if ($resources)
        {
            $resources = array_keys($this->_config->resources->toArray());
            foreach ($resources as $resourceName) {
                $options = $this->_config->resources->$resourceName;
                $configuratorClass = 'WJB_Application_Module_Configurator_' . ucfirst($resourceName);
                $configurator = new $configuratorClass($options);
                $configurator->setBootstrap($this->_bootstrap);
                $configurator->init();
            }
        }

    }

}