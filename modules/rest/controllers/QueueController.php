<?php

use WJB\Service\Artist as ArtistService;


class Rest_QueueController extends WJB\Rest\Controller
{

    public function init()
    {
        parent::init();
    }

    public function indexAction()
    {

        $channelId = $this->getRequest()->getParam('channel_id');

        $queueService = new \WJB\Service\Queue();
        $queue = $queueService->getByChannel($channelId);

        $result = array();
        foreach ($queue as $entry)
        {
            $result[] = array(
                'queue_id' => $entry->getId(),
                'queue_position' => $entry->getPosition(),
                'user_id' => $entry->getUserId(),
                'user_name' => $entry->getUser()->getFullname(),
                'song' => $entry->getSong()->toArray(true),
                'class' => 'queue'
            );
        }

        $this->view->payload = $result;
        $this->getResponse()
            ->setHttpResponseCode(200);

    }

    public function postAction()
    {

        $auth = Zend_Registry::get('auth');

        $queueService = new \WJB\Service\Queue();
        $channelId = (int) $this->getRequest()->getParam('channel_id', $auth['channel_id']);
        $userId = (int) $this->getRequest()->getParam('user_id', $auth['id']);

        $songId = (int) $this->getRequest()->getParam('song_id', null);
        $albumId = (int) $this->getRequest()->getParam('album_id', null);

        if ($songId != null)
            $queueService->addSong($songId, $channelId, $userId);
        elseif ($albumId != null)
            $queueService->addAlbum($albumId, $channelId, $userId);

    }

}

