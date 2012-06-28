<?php

class WJB_Controller_Plugin_ModuleConfigurator extends Zend_Controller_Plugin_Abstract
{

    public function preDispatch(Zend_Controller_Request_Abstract $request)
    {

        $front = Zend_Controller_Front::getInstance();
        $bootstrap = $front->getParam('bootstrap');
        $moduleName = $request->getModuleName();
        if ($moduleName == $front->getDefaultModule()) {
            return;
        }
        $moduleDirectory = Zend_Controller_Front::getInstance()
            ->getModuleDirectory($moduleName);
        $configPath = $moduleDirectory . '/configs/module.ini';
        if (file_exists($configPath)) {
            if (!is_readable($configPath)) {
                throw Exception('modules.ini not readable for module "' . $moduleName . '"');
            }
            $config = new Zend_Config_Ini($configPath, $bootstrap->getEnvironment());
            $configurator = new WJB_Application_Module_Configurator($config);
            $configurator->run();

        }

    }

}
