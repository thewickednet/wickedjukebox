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


}

