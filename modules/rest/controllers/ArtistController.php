<?php

use WJB\Service\Artist as ArtistService;
use WJB\Rest\Uri as Uri;

class Rest_ArtistController extends WJB\Rest\Controller
{

    public function init()
    {
        parent::init();
    }

    public function getAction()
    {

        $id = $this->getRequest()->getParam('id');

        $artistService = new ArtistService();
        $artist = $artistService->getById($id)->toArray(true);

        $this->view->payload = $artist;

        $this->getResponse()
            ->setHttpResponseCode(200);

    }


}

