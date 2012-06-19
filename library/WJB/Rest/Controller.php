<?php

namespace WJB\Rest;

class Controller extends \Zend_Rest_Controller
{

    public $id = null;
    public $body = '';
    public $deep = true;

    private $_log = null;

    public function init()
    {
        $this->_log = \Zend_Registry::get('log');
        $contextSwitch = $this->_helper->getHelper('contextSwitch');
        $contextSwitch->addActionContext($this->getRequest()->getActionName(), array('json'));
        $contextSwitch->setAutoJsonSerialization(true);
        $contextSwitch->initContext('json');
    }

    public function indexAction()
    {
        $this->getResponse()
            ->setHttpResponseCode(501);
    }

    public function getAction()
    {
        $this->getResponse()
            ->setHttpResponseCode(501);
    }

    public function postAction()
    {
        $this->getResponse()
            ->setHttpResponseCode(501);
    }

    public function putAction()
    {
        $this->getResponse()
            ->setHttpResponseCode(501);
    }

    public function deleteAction()
    {
        $this->getResponse()
            ->setHttpResponseCode(501);
    }

    public function postDispatch() {
        parent::postDispatch();
        $this->view->ref = $this->getRequest()->getParam('ref', null);
        $logLine = sprintf("%s %s (%s)\t%s\nRaw Body: %s\nParams:\n%s\n",
            $this->getRequest()->getControllerName(),
            $_SERVER['REMOTE_ADDR'],
            $this->getRequest()->getActionName(),
            $this->id,
            $this->getRequest()->getRawBody(),
            print_r($this->getRequest()->getParams(), true));
        $this->_log->debug($logLine);
        $logLine = sprintf("Sending back:\n%s\n",
            print_r($this->view->payload, true));
        $this->_log->debug($logLine);
    }

}
