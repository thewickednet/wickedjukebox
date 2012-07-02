<?php

namespace WJB\Entity\Repository;

use Doctrine\ORM\EntityRepository;

/**
 * QueueRepository
 *
 * This class was generated by the Doctrine ORM. Add your own custom
 * repository methods below.
 */
class QueueRepository extends EntityRepository
{


    public function getLastPosition($channelId)
    {
        $em = $this->getEntityManager();
        $qb = $em->createQueryBuilder();

        $qb->select('q.position')
            ->from('\WJB\Entity\Queue', 'q')
            ->where('q.channelId = :channelId')
            ->orderBy('q.position', 'DESC')
            ->setMaxResults(1)
            ->setParameter('channelId', $channelId);

        $query = $qb->getQuery();
        $result = $query->getSingleResult();

        return $result['position'];
    }


}
