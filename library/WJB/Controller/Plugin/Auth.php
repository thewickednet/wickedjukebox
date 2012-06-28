<?php

class WJB_Controller_Plugin_Auth extends Zend_Controller_Plugin_Abstract
{

    private $_em;
    private $_auth;

    public function preDispatch(Zend_Controller_Request_Abstract $request)
    {

        $this->_auth = Zend_Auth::getInstance();
        $front = Zend_Controller_Front::getInstance();
        $this->_em = $front->getParam('bootstrap')->getResource('doctrine')->getEntityManager();;

        $res = false;
        switch ($request->getModuleName())
        {
            case "rest":
                $res = $this->handleRestAuth($request);
            break;
            default:
                $res = $this->handleDefaultAuth($request);
        }
        Zend_Registry::set('auth', $res);
    }


    private function handleRestAuth($request)
    {

        $auth = $request->getHeader('Authorization');
        if ($auth)
        {
            $auth = str_replace('Basic ', '', $auth);
            $auth = base64_decode($auth);
            list ($username, $password) = explode(":", $auth);
            $user = $this->_em->getRepository('\WJB\Entity\User')->findOneByUsername($username);
            if (md5($password) == $user->getPassword())
            {
                return $user->toArray();
            }
        }
        $reponse = new Zend_Controller_Response_Http();
        $reponse->setHeader('WWW-Authenticate', 'Basic realm="WJB"')
                ->setHttpResponseCode(401);
        $reponse->sendResponse();
        exit();
    }


    private function handleDefaultAuth($request)
    {

        $controller = $request->getControllerName();

        if ($controller != 'auth')
        {
            if (!$this->_auth->hasIdentity())
            {
                $request->setModuleName($request->getModuleName());
                $request->setControllerName('auth');
                $request->setActionName('login');
            }
            else
            {
                $identity = $this->_auth->getIdentity();
                $user = $this->_em->getRepository('\WJB\Entity\User')->findOneByUsername($identity);
                return $user->toArray();
            }
        }
        return false;
    }


}

