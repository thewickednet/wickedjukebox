<?php

namespace WJB;

abstract class Service {

    /**
     * @var null|EntityManager
     */
    protected $_entityManager = null;

    public function __construct()
    {
        $bootstrap = \Zend_Controller_Front::getInstance()->getParam('bootstrap');
        $this->_entityManager = $bootstrap->getResource('doctrine')->getEntityManager();
    }

    public function getEm()
    {
        return $this->_entityManager;
    }

    public function getRepo($repo)
    {
        return $this->_entityManager->getRepository($repo);
    }

}