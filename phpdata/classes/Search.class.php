<?php

class Search {

    function byArtist($pattern = "a") {
        
        $db = Zend_Registry::get('database');
        
        $pattern = sprintf("%%%s%%", $pattern);
        
        $select = $db->select()
                     ->from(array('s' => 'song'), array('song_id' => 'id', 'song_name' => 'title', 'duration'))
                     ->join(array('ar' => 'artist'), 's.artist_id = ar.id', array('artist_id' => 'id', 'artist_name' => 'name'))
                     ->joinLeft(array('al' => 'album'), 's.album_id = al.id', array('album_id' => 'id', 'album_name' => 'name'))
                     ->where('ar.name like ?', $pattern)
                     ->order('ar.name', 'al.name');

        $stmt = $select->query();
        $result = $stmt->fetchAll();

        for ($i = 0; $i < count($result); $i++) {
            $id = $result[$i]['song_id'];
            $result[$i]['standing'] = User::getStanding($id);
        }

        return $result;
    }

    function byAlbum($pattern = "a") {
        
        $db = Zend_Registry::get('database');
        
        $pattern = sprintf("%%%s%%", $pattern);
        
        $select = $db->select()
                     ->from(array('s' => 'song'), array('song_id' => 'id', 'song_name' => 'title', 'duration'))
                     ->join(array('ar' => 'artist'), 's.artist_id = ar.id', array('artist_id' => 'id', 'artist_name' => 'name'))
                     ->joinleft(array('al' => 'album'), 's.album_id = al.id', array('album_id' => 'id', 'album_name' => 'name'))
                     ->where('al.name like ?', $pattern)
                     ->order('ar.name', 'al.name');

        $stmt = $select->query();
        $result = $stmt->fetchAll();

        for ($i = 0; $i < count($result); $i++) {
            $id = $result[$i]['song_id'];
            $result[$i]['standing'] = User::getStanding($id);
        }

        return $result;
    }

    function bySong($pattern = "a", $limit = 0) {
        
        $db = Zend_Registry::get('database');
        $core   = Zend_Registry::get('core');
        
        $pattern = sprintf("%%%s%%", $pattern);
        
        $select = $db->select()
                     ->from(array('s' => 'song'), array('song_id' => 'id', 'song_name' => 'title', 'duration'))
                     ->join(array('ar' => 'artist'), 's.artist_id = ar.id', array('artist_id' => 'id', 'artist_name' => 'name'))
                     ->joinleft(array('al' => 'album'), 's.album_id = al.id', array('album_id' => 'id', 'album_name' => 'name'))
                     ->where('s.title like ?', $pattern)
                     ->order('ar.name', 'al.name')
                     ->limit($limit);
        

        $stmt = $select->query();
        $result = $stmt->fetchAll();
        
        for ($i = 0; $i < count($result); $i++) {
            $id = $result[$i]['song_id'];
            $result[$i]['standing'] = User::getStanding($id);
        }
        
        return $result;
    }

    function byLyrics($pattern = "a") {
        
        $db = Zend_Registry::get('database');
        
        $pattern = sprintf("%%%s%%", $pattern);
        
        $select = $db->select()
                     ->from(array('s' => 'song'), array('song_id' => 'id', 'song_name' => 'title', 'duration'))
                     ->join(array('ar' => 'artist'), 's.artist_id = ar.id', array('artist_id' => 'id', 'artist_name' => 'name'))
                     ->joinleft(array('al' => 'album'), 's.album_id = al.id', array('album_id' => 'id', 'album_name' => 'name'))
                     ->where('s.lyrics like ?', $pattern)
                     ->order('ar.name', 'al.name');

        $stmt = $select->query();
        $result = $stmt->fetchAll();

        for ($i = 0; $i < count($result); $i++) {
            $id = $result[$i]['song_id'];
            $result[$i]['standing'] = User::getStanding($id);
        }

        return $result;
    }

    function byAny($pattern = "a") {
        
        $db = Zend_Registry::get('database');
        
        $pattern = sprintf("%%%s%%", $pattern);

        $select = $db->select()
                     ->from(array('s' => 'song'), array('song_id' => 'id', 'song_name' => 'title', 'duration'))
                     ->join(array('ar' => 'artist'), 's.artist_id = ar.id', array('artist_id' => 'id', 'artist_name' => 'name'))
                     ->joinleft(array('al' => 'album'), 's.album_id = al.id', array('album_id' => 'id', 'album_name' => 'name'))
                     ->where('s.title like ?', $pattern)
                     ->orWhere('al.name like ?', $pattern)
                     ->orWhere('ar.name like ?', $pattern)
                     ->order('ar.name', 'al.name');

        $stmt = $select->query();
        $result = $stmt->fetchAll();

        for ($i = 0; $i < count($result); $i++) {
            $id = $result[$i]['song_id'];
            $result[$i]['standing'] = User::getStanding($id);
        }

        return $result;
    }

}



?>