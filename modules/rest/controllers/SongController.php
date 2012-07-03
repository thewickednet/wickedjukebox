<?php

use WJB\Service\Song as SongService;
use WJB\Rest\Uri as Uri;

class Rest_SongController extends WJB\Rest\Controller
{

    public function init()
    {
        parent::init();
    }

    public function getAction()
    {

        $id = $this->getRequest()->getParam('id');

        $songService = new SongService();
        $song = $songService->getById($id)->toArray(true);

        $this->view->payload = $song;

        $this->getResponse()
            ->setHttpResponseCode(200);

    }


}

