<?php

use WJB\Service\Channel as ChannelService;
use WJB\Service\Song as SongService;


class Rest_ChannelController extends WJB\Rest\Controller
{

    public function init()
    {
        parent::init();
    }

    public function indexAction()
    {

        $channelService = new \WJB\Service\Channel();
        $channels = $channelService->getAll();

        $results = array();
        foreach ($channels as $channel)
        {
            if ($channel->getPublic() == 0)
                continue;
            $results[] = $channelService->toArray($channel);

        }
        $this->view->payload = $results;
        $this->getResponse()
            ->setHttpResponseCode(200);

    }


    public function getAction()
    {

        $id = $this->getRequest()->getParam('id');

        $channelService = new ChannelService();
        $channel = $channelService->getById($id);

        $this->view->payload = $channelService->toArray($channel);
        $this->getResponse()
            ->setHttpResponseCode(200);

    }


    private function channelDataToArray($channel)
    {

        $songService = new \WJB\Service\Song();
        $current = array(
            'progress' => null,
            'song' => null
        );

        $states = $channel->getStates();
        foreach ($states as $state)
        {
            switch ($state->getState())
            {
                case "progress":
                    break;
                case "current_song":
                    $song = $songService->getById($state->getValue());
                    $artist = $song->getArtist();
                    //$album = $song->getAlbum;
                    $songArray = array(
                        'song_id' => $song->getId(),
                        'song_title' => $song->getTitle(),
                        'song_duration' => $song->getDuration(),
                        'artist_id' => $artist->getId(),
                        'artist_name' => $artist->getName()
                    );
                    $current['song'] = $songArray;
                    break;
            }
            if ($state->getState() == 'progress')
                $current['progress'] = (double) $state->getValue();
        }

        return array(
            'id' => $channel->getId(),
            'name' => $channel->getName(),
            'backend' => $channel->getBackend(),
            'current' => $current
        );

    }

}

