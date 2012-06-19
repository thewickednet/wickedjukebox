<?php

class Rest_ChannelController extends WJB\Rest\Controller
{

    private $_em;

    public function init()
    {
        parent::init();
        $this->_em = $this->getInvokeArg('bootstrap')->getResource('doctrine')->getEntityManager();
        $this->_channelRep = $this->_em->getRepository('\WJB\Entity\Channel');
    }

    public function indexAction()
    {
        $results = array();
        $channels = $this->_channelRep->findAll();

        foreach ($channels as $channel)
        {
            $results[] = array(
                'name' => $channel->getName(),
                'backend' => $channel->getBackend(),
                'public' => $channel->getPublic()
            );
        }
        $this->view->payload = $results;
        $this->getResponse()
            ->setHttpResponseCode(200);

    }



}
