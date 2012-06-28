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
        $doctrine = \Zend_Registry::get('doctrine');
        $this->_entityManager = $doctrine->getEntityManager();
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