<?php

class Artist {


    function getByAlpha($alpha = "a", $threshold = 2) {
        
        $db = Zend_Registry::get('database');
        

        $select = $db->select()
                     ->from(array('a' => 'artist'), array('id', 'name', 'added'))
                     ->join(array('s' => 'song'), 's.artist_id = a.id', array('songs' => 'COUNT(*)'))
                     ->group('a.name')
                     ->where('substr(name, 1, 1) = ?', $alpha)
                     ->having('songs > ?', $threshold)
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
                     ->from(array('s' => 'song'), array('title', 'song_id' => 'id', 'track_no', 'duration', 'localpath'))
                     ->joinLeft(array('a' => 'album'), 's.album_id = a.id', array('album_name' => 'name', 'album_id' => 'id'))
                     ->where('s.artist_id = ?', $artist_id)
                     ->order('album_name', 'track_no');
                     
        $stmt = $select->query();
        $result = $stmt->fetchAll();
        return $result;
        
    }



  function findCover($artist_id = 0){

    $filemasks = array('/../../folder.jpg', '/../../Folder.jpg','/../folder.jpg', '/../Folder.jpg', '/../folder.png', '/../Folder.png', '/../folder.gif', '/../Folder.gif', '/artist.jpg');

    $songs = self::getSongs($artist_id);
    foreach($songs as $song) {
      foreach($filemasks as $filemask){
        $check = dirname($song['localpath']) . $filemask;
        if (file_exists($check))
          return $check;
      }

    }

    return "";

  }

    function getTotalCount() {
    	
        $db     = Zend_Registry::get('database');
        
        $query = "SELECT COUNT(*) AS counter FROM artist";
        
        $result = $db->fetchOne($query);
        return $result;
    	
    }
    
    function getSongCount() {
        
        $db     = Zend_Registry::get('database');
        
        $query = "SELECT COUNT(*) AS counter, artist.id AS artist_id, artist.name AS artist_name FROM song JOIN artist ON song.artist_id=artist.id GROUP BY artist_id ORDER BY counter DESC LIMIT 10";
        
        $result = $db->fetchAll($query);
        return $result;
        
        
    }

    function getAlbumCount() {
        
        $db     = Zend_Registry::get('database');
        
        $query = "SELECT COUNT(*) AS counter, artist.id AS artist_id, artist.name AS artist_name FROM album JOIN artist ON album.artist_id=artist.id GROUP BY artist_id ORDER BY counter DESC LIMIT 10";
        
        $result = $db->fetchAll($query);
        return $result;
        
        
    }


}


?>