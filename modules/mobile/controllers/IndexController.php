<?php

use WJB\Service\Queue as QueueService;
use WJB\Service\Channel as ChannelService;


class Mobile_IndexController extends Zend_Controller_Action {

    private $_auth = false;

    public function init()
    {
        $this->view->headerString = 'Welcome';
        $this->_auth = Zend_Registry::get('auth');
    }

    public function indexAction()
    {

        $ajax = $this->getRequest()->getParam('ajax', false);
        if ($ajax)
            $this->_helper->layout->disableLayout();


        $queueService = new QueueService();
        $queue = $queueService->getByChannel($this->_auth['channel_id']);

        $channelService = new ChannelService();
        $channel = $channelService->getById($this->_auth['channel_id']);

        $this->view->auth = $this->_auth;
        $this->view->channel = $channelService->toArray($channel);
        $this->view->queue = $queue;


    }


}
