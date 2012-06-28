<?php


class Mobile_AuthController extends Zend_Controller_Action {

    public function indexAction()
    {
        $this->_helper->redirector('login');
    }


    public function loginAction()
    {

        if (Zend_Auth::getInstance()->hasIdentity()) {
            $this->_helper->redirector('index', 'index', 'mobile');
            exit();
        }

        $form = new WJB_Form_Login();
        $form->setAction('/mobile/auth/login');

        if ($this->_request->isPost()) {
            # get params
            $data = $this->_request->getPost();
            # check validate form
            if ($form->isValid($data)) {
                # attempt to authentication
                $auth_service = new WJB_Service_Auth($data['username'], $data['password']);
                $auth = Zend_Auth::getInstance()->authenticate($auth_service);
                $this->view->priorityMessenger($auth->getMessages() , $auth->getCode());
                if ($auth->isValid())
                    $this->_helper->redirector('index', 'index', 'mobile');
            }
            $form->populate($data);
        }

        $this->view->form = $form;
        $this->view->headerString = 'Welcome';

    }


    /**
     * The default action - show the home page
     */
    public function logoutAction()
    {
        $auth = Zend_Auth::getInstance();
        $auth->clearIdentity();
        $this->_redirect('/');

    }


}
