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

        $pattern = $this->getRequest()->getParam('pattern');

        $searchService = new SearchService();
        $search = $searchService->execute($pattern, true);

        $this->view->payload = $search;

        $this->getResponse()
            ->setHttpResponseCode(200);

    }


}

