<?php

namespace WJB\Service;

class Channel extends \WJB\Service {


    public function __construct()
    {
        parent::__construct();
        $this->setDefaultRepo('\WJB\Entity\Channel');
    }


    public function toArray($channel)
    {

        $songService = new \WJB\Service\Song();
        $current = array();

        $states = $channel->getStates();
        foreach ($states as $state)
        {
            switch ($state->getState())
            {
                case "progress":
                break;
                case "current_song":
                    $current['song'] = $songService->getById($state->getValue())->toArray(true);
                break;
            }
            if ($state->getState() == 'progress')
                $current['progress'] = (double) $state->getValue();
        }

        return array(
            'id' => $channel->getId(),
            'name' => $channel->getName(),
            'backend' => $channel->getBackend(),
            'current' => $current,
            'class' => 'channel'
        );

    }

}
