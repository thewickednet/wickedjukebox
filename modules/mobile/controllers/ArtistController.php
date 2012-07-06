<?php

use WJB\Service\Artist as ArtistService;

class Mobile_ArtistController extends Zend_Controller_Action
{

    public function init()
    {
        $this->view->headerString = 'Artist';
    }

    public function detailAction()
    {
        $id = $this->getRequest()->getParam('id');

        $artistService = new ArtistService();
        $this->view->artist = $artistService->getById($id);
    }

}

