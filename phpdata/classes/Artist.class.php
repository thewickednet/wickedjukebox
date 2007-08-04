<?php

class Artist {


    function getByAlpha($alpha = "a") {
        
        $db = Zend_Registry::get('database');
        
        $select = $db->select()
                     ->distinct()
                     ->from(array('a' => 'artist'), array('id', 'name'))
                     ->where('substr(name, 1, 1) = ?', $alpha);
                     
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
        
        
        
        
        
    }

    function getSongs($artist_id = null) {
        
        $db = Zend_Registry::get('database');
        
        $select = $db->select('*, album.id AS album_id, s.id AS song_id')
                     ->from(array('s' => 'song'), array('title', 'song_id' => 'id'))
                     ->joinLeft(array('a' => 'album'), 's.album_id = a.id')
                     ->where('s.artist_id = ?', $artist_id)
                     ->order('name', 'track_no');
                     
                     
        $stmt = $select->query();
        $result = $stmt->fetchAll();
        return $result;
        
    }






}



?>