<?php

use WJB\Service\Search as SearchService;

class Rest_SearchController extends WJB\Rest\Controller
{

    public function init()
    {
        parent::init();
    }

    public function indexAction()
    {

        $query = $this->getRequest()->getParam('q');

        $searchService = new SearchService();
        $searchService->execute($query);

        $this->view->payload = $searchService->getHitsArray();

        $this->getResponse()
            ->setHttpResponseCode(200);

    }


}

