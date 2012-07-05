<?php

use WJB\Service\Album as AlbumService;
use WJB\Service\Queue as QueueService;

class Mobile_AlbumController extends Zend_Controller_Action
{

    public function init()
    {

    }

    public function detailAction()
    {
        $id = $this->getRequest()->getParam('id');

        $albumService = new AlbumService();
        $this->view->album = $albumService->getById($id);
    }

    public function queueAction()
    {
        $id = $this->getRequest()->getParam('id');

        $auth = Zend_Registry::get('auth');
        $queueService = new QueueService();
        $queueService->addAlbum($id, $auth['channel_id'], $auth['id']);
        $this->_forward('detail', 'album', 'mobile', array('id' => $id));

    }

}

