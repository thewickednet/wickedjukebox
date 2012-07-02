<?php

namespace WJB\Service;


class Queue extends \WJB\Service {


    public function __construct()
    {
        parent::__construct();
        $this->setDefaultRepo('\WJB\Entity\Queue');
    }


    public function getByChannel($channelId)
    {
        $qb = $this->getEm()->createQueryBuilder();
        $qb->select('q')
            ->from('\WJB\Entity\Queue', 'q')
            ->where($qb->expr()->andX(
                $qb->expr()->eq('q.channelId', ':channelId'),
                $qb->expr()->gt('q.position', ':position')
            ))
            ->orderBy('q.position', 'ASC');
        $qb->setParameter('channelId', $channelId);
        $qb->setParameter('position', 0);

        $query = $qb->getQuery();
        $res = $query->getResult();
        return $res;
    }

    public function addSong($songId, $channelId, $userId)
    {

        $position = $this->getRepo()->getLastPosition($channelId) + 1;

        $songService = new \WJB\Service\Song();
        $song = $songService->getById($songId);

        $channelService = new \WJB\Service\Channel();
        $channel = $channelService->getById($channelId);

        $userService = new \WJB\Service\User();
        $user = $userService->getById($userId);

        $this->addToQueue($song, $user, $channel, $position);
        $this->getEm()->flush();
    }


    public function addAlbum($albumId, $channelId, $userId)
    {
        $position = $this->getRepo()->getLastPosition($channelId) + 1;

        $albumService = new \WJB\Service\Album();
        $album = $albumService->getById($albumId);

        $channelService = new \WJB\Service\Channel();
        $channel = $channelService->getById($channelId);

        $userService = new \WJB\Service\User();
        $user = $userService->getById($userId);

        foreach ($album->getSongs() as $song)
        {
            $position++;
            $this->addToQueue($song, $user, $channel, $position);
        }
        $this->getEm()->flush();

    }

    private function addToQueue($song, $user, $channel, $position)
    {
        $q = new \WJB\Entity\Queue();
        $q->setChannel($channel);
        $q->setUser($user);
        $q->setSong($song);
        $q->setPosition($position);
        $q->setAdded(new \DateTime("now"));
        $this->getEm()->persist($q);

    }


}

