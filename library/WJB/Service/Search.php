<?php

namespace WJB\Service;


class Search {

    private $_lucene = null;

    public function __construct()
    {
        $this->_lucene = Zend_Search_Lucene::open(APPLICATION_ROOT . '/data/lucence');
    }

    public function execute($pattern)
    {
        return $this->_lucene->find($pattern);
    }

}
