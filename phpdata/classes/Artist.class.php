<?php

class Artist {


    function getByAlpha($alpha = "a") {
        
        $db = Zend_Registry::get('database');
        
        $select = $db->select()
                     ->distinct()
                     ->from(array('a' => 'artist'), array('id', 'name'))
                     ->where('substr(name, 1, 1) = ?', $alpha)
                     ->order('name');

        $stmt = $select->query();
        $result = $stmt->fetchAll();
        return $result;
    }


    function getById($artist_id = null) {
        
        $db = Zend_Registry::get('database');
        
        $select = $db->select()
                     ->from('artist')
                     ->where('id = ?', $artist_id);
                     
        $stmt = $select->query();
        $result = $stmt->fetchAll();
        return $result[0];
    }

    function getAlbums($artist_id = null) {
        
        $db = Zend_Registry::get('database');
        
        $select = $db->select()
                     ->from(array('a' => 'album'))
                     ->where('a.artist_id = ?', $artist_id)
                     ->order('name');
                     
        $stmt = $select->query();
        $result = $stmt->fetchAll();
        return $result;
        
    }

    function getSongs($artist_id = null) {
        
        $db = Zend_Registry::get('database');
        
        $select = $db->select()
                     ->from(array('s' => 'song'), array('title', 'song_id' => 'id', 'track_no', 'duration'))
                     ->joinLeft(array('a' => 'album'), 's.album_id = a.id', array('album_name' => 'name', 'album_id' => 'id'))
                     ->where('s.artist_id = ?', $artist_id)
                     ->order('album_name', 'track_no');
                     
        $stmt = $select->query();
        $result = $stmt->fetchAll();
        return $result;
        
    }






}



?>