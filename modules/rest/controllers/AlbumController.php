<?php

use WJB\Service\Album as AlbumService;
use WJB\Rest\Uri as Uri;

class Rest_AlbumController extends WJB\Rest\Controller
{

    public function init()
    {
        parent::init();
    }

    public function getAction()
    {

        $id = $this->getRequest()->getParam('id');

        $abumService = new AlbumService();
        $album = $abumService->getById($id)->toArray(true);

        $this->view->payload = $album;

        $this->getResponse()
            ->setHttpResponseCode(200);

    }


}

