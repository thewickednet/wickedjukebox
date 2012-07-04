<?php

namespace WJB\Service;

use WJB\Service\Artist as ArtistService;
use WJB\Service\Album as AlbumService;
use WJB\Service\Song as SongService;


class Search {

    private $_lucene = null;
    private $_hits = null;

    public function __construct()
    {
        $options = \Zend_Controller_Front::getInstance()->getParam('bootstrap')->getApplication()->getOption('lucene');
        $this->_lucene = \Zend_Search_Lucene::open($options['index_path']);
    }


    public function execute($pattern)
    {
        $this->_hits = $this->_lucene->find($pattern);
    }


    public function getHitsArray()
    {
        $data = array();
        foreach ($this->_hits as $hit)
        {
            $item = unserialize($hit->data);
            $item['score'] = $hit->score;
            $data[] = $item;
        }
        return $data;
    }


    public function getHits()
    {
        return $this->_hits;
    }

}
