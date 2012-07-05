<?php

use WJB\Service\Search as SearchService;

class Mobile_SearchController extends Zend_Controller_Action
{

    private $_em;

    public function init()
    {
        $this->_em = $this->getInvokeArg('bootstrap')->getResource('doctrine')->getEntityManager();
        /* Initialize action controller here */
    }

    public function indexAction()
    {

        $q = $this->getRequest()->getParam('q', '');

        $hits = array();

        if (strlen($q) > 3)
        {
            $searchService = new SearchService();
            $searchService->execute($q);
            $hits = $searchService->getHits();
        }
        $this->view->hits = $hits;
        $this->view->searchQuery = $q;

    }


}

