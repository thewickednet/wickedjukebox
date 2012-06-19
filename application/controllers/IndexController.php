<?php

class IndexController extends Zend_Controller_Action
{

    private $_em;

    public function init()
    {
        $this->_em = $this->getInvokeArg('bootstrap')->getResource('doctrine')->getEntityManager();
        /* Initialize action controller here */
    }

    public function indexAction()
    {

        $this->view->artist = $this->_em->getRepository('\WJB\Entity\Artist')->find(4);



    }


}

