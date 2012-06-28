<?php

namespace WJB;

abstract class Service {

    /**
     * @var null|EntityManager
     */
    protected $_entityManager = null;
    protected $_defaultRepo = null;

    public function __construct()
    {
        $bootstrap = \Zend_Controller_Front::getInstance()->getParam('bootstrap');
        $this->_entityManager = $bootstrap->getResource('doctrine')->getEntityManager();
    }

    public function getEm()
    {
        return $this->_entityManager;
    }

    public function getRepo($repo = null)
    {
        if ($repo == null)
            $repo = $this->_defaultRepo;
        return $this->_entityManager->getRepository($repo);
    }

    public function setDefaultRepo($name)
    {
        $this->_defaultRepo = $name;
    }

    public function getAll()
    {
        return $this->getRepo()->findAll();
    }

    public function getById($id)
    {
        return $this->getRepo()->find($id);
    }



}