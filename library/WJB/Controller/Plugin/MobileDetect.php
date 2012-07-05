<?php

class WJB_Controller_Plugin_MobileDetect extends Zend_Controller_Plugin_Abstract {

    public function preDispatch(Zend_Controller_Request_Abstract $request)
    {
        $module = $request->getModuleName();

        if ($module == 'mobile')
            return;

        $browser = get_browser();

        $controller = $request->getControllerName();
        $action = $request->getActionName();

        if ($browser && $browser->ismobiledevice == 1) {
            return $request->setModuleName("mobile")
                           ->setControllerName($controller)
                           ->setActionName($action)
                           >setDispatched(true);

        }

        return;
    }
}
