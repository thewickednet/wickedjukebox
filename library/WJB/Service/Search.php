<?php

namespace WJB\Service;

use WJB\Service\Artist as ArtistService;
use WJB\Service\Album as AlbumService;
use WJB\Service\Song as SongService;


class Search {

    private $_lucene = null;

    public function __construct()
    {
        $options = \Zend_Controller_Front::getInstance()->getParam('bootstrap')->getApplication()->getOption('lucene');
        $this->_lucene = \Zend_Search_Lucene::open($options['index_path']);
    }

    public function execute($pattern, $toArray = false)
    {
        $hits = $this->_lucene->find($pattern);

        if ($toArray)
        {
            $data = array();

            foreach ($hits as $hit)
            {
                $item = unserialize($hit->data);
                $item['score'] = $hit->score;
                $data[] = $item;
            }
            return $data;

        }

        return $hits;
    }


    private function transformEntry($entry)
    {
        switch($entry->class)
        {
            case "artist":
                return array(
                    'class' => 'artist',
                    'id' => (int) $entry->key,
                    'name' => $entry->artist,
                    'score' => $entry->score
                );
            break;
            case "album":
                return array(
                    'class' => 'album',
                    'id' => (int) $entry->key,
                    'name' => $entry->album,
                    'artist' => $entry->artist,
                    'score' => $entry->score
                );
            break;
            case "song":
                return array(
                    'class' => 'song',
                    'id' => (int) $entry->key,
                    'title' => $entry->song,
                    'artist' => $entry->artist,
                    'score' => $entry->score
                );
            break;
        }
    }


}
