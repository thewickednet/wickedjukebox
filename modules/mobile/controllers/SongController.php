<?php

use WJB\Service\Song as SongService;
use WJB\Service\Queue as QueueService;

class Mobile_SongController extends Zend_Controller_Action
{

    public function init()
    {
        $this->view->headerString = 'Song';
    }

    public function detailAction()
    {
        $id = $this->getRequest()->getParam('id');

        $songService = new SongService();
        $this->view->song = $songService->getById($id);
    }

    public function queueAction()
    {
        $id = $this->getRequest()->getParam('id');

        $auth = Zend_Registry::get('auth');

        $queueService = new QueueService();
        $queueService->addSong($id, $auth['channel_id'], $auth['id']);
        $this->_forward('detail', 'song', 'mobile', array('id' => $id));

    }

}

