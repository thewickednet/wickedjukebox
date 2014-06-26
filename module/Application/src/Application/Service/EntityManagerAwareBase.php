<?php

namespace Application\Service;

use Zend\ServiceManager\ServiceManagerAwareInterface;
use Zend\ServiceManager\ServiceManager;
use Doctrine\ORM\EntityManager;


class EntityManagerAwareBase extends Base implements ServiceManagerAwareInterface
{

    /**
     * @var EntityManager
     */
    protected $em;

    /**
     * @param EntityManager $em
     */
    public function __construct(EntityManager $em)
    {
        $this->em      = $em;
    }

    /**
     * Retrieve entity manager instance
     *
     * @return EntityManager
     */
    public function getEntityManager()
    {
        return $this->em;

    }

}