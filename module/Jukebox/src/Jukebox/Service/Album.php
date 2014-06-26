<?php

namespace Jukebox\Service;

use Zend\Form\Form;
use Zend\Crypt\Password\Bcrypt;
use Zend\Stdlib\Hydrator;
use DoctrineModule\Stdlib\Hydrator\DoctrineObject as DoctrineHydrator;

class Album extends \Application\Service\EntityManagerAwareBase
{

    public function getById($id)
    {
        $fr = $this->em->getRepository('Jukebox\Entity\Album');
        return $fr->find($id);
    }

}