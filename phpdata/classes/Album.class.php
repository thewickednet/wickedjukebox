<?php

class Album {

    function getAll() {
        
        $db = Zend_Registry::get('database');
        
            $select = $db->select()
                         ->from(array('a' => 'album'));
    
        $stmt = $select->query();
        $result = $stmt->fetchAll();
        return $result;
    }

    function getByAlpha($alpha = "a") {
        
        $db = Zend_Registry::get('database');
        
        if ($alpha == 'ost' || $alpha == 'various' || $alpha == 'game') {
            
            $select = $db->select()
                         ->distinct()
                         ->from(array('a' => 'album'), array('album_id' => 'id', 'album_name' => 'name', 'type'))
                         ->join(array('ar' => 'artist'), 'a.artist_id = ar.id', array('artist_id' => 'id', 'artist_name' => 'name'))
                         ->join(array('s' => 'song'), 's.album_id = a.id', array('songs' => 'COUNT(*)'))
                         ->where('a.type = ?', $alpha)
                         ->group('a.name')
                         ->order('a.name');

        } else {
                
            $select = $db->select()
                         ->distinct()
                         ->from(array('a' => 'album'), array('album_id' => 'id', 'album_name' => 'name', 'type'))
                         ->join(array('ar' => 'artist'), 'a.artist_id = ar.id', array('artist_id' => 'id', 'artist_name' => 'name'))
                         ->join(array('s' => 'song'), 's.album_id = a.id', array('songs' => 'COUNT(*)'))
                         ->where('substr(a.name, 1, 1) = ?', $alpha)
                         ->where('a.type = ?', 'album')
                         ->group('a.name')
                         ->order('a.name');
    
        
        }
        
        $stmt = $select->query();
        $result = $stmt->fetchAll();
        return $result;
    }

    function getSongs($album_id = null) {

        $db = Zend_Registry::get('database');
        
        $select = $db->select()
                     ->from(array('s' => 'song'))
                     ->join(array('ar' => 'artist'), 's.artist_id = ar.id', array('artist_id' => 'id', 'artist_name' => 'name'))
                     ->where('s.album_id = ?', $album_id)
                     ->order('track_no', 'title');

        $stmt = $select->query();
        $result = $stmt->fetchAll();
        
        for ($i = 0; $i < count($result); $i++) {
            $id = $result[$i]['id'];
            $result[$i]['standing'] = User::getStanding($id);
        }
        
        return $result;

    }


    function getById($album_id = null) {
        if (!isset($album_id))
            return array();


        $db = Zend_Registry::get('database');

        $select = $db->select()
                     ->from('album')
                     ->where('id = ?', $album_id);
                     
        $stmt = $select->query();
        $result = $stmt->fetchAll();
        if (count($result) == 1)
            return $result[0];
        return array();
    }

  function findCover($album_id = 0){

    $filemasks = array('folder.jpg', 'Folder.jpg', 'cover.jpg', 'Cover.jpg', 'folder.gif', 'Folder.gif', 'Folder.png', 'folder.png', 'cover.png', 'Cover.png');

    $songs = self::getSongs($album_id);
    foreach($songs as $song) {
      foreach($filemasks as $filemask){
        $check = dirname($song['localpath']) . '/' . $filemask;
	$check = utf8_encode($check);
        if (file_exists($check))
          return $check;
      }

    }

    return "";

  }


    function getCost($album_id) {
        $db = Zend_Registry::get('database');
        
        $select = $db->select()
                     ->from(array('s' => 'song'), array('cduration' => 'SUM(duration)'))
                     ->where('s.album_id = ?', $album_id);
                     
        $stmt = $select->query();
        $result = $stmt->fetchAll();
        if (count($result) == 1)
            return round($result[0]['cduration']/60);
        return 0;
        
    }

    function getTotalCount() {
    	
        $db     = Zend_Registry::get('database');
        
        $select = $db->select()
                     ->from(array('a' => 'album'), array('counter' => 'COUNT(*)'));
    
        $stmt = $select->query();
        $result = $stmt->fetchAll();
        return $result[0]['counter'];
    	
    }
    
    function getPlays() {
    	
        $db     = Zend_Registry::get('database');
        
        $query = "SELECT COUNT(*) as counter, album.*, album.id AS album_id, album.name AS album_name, artist.id AS artist_id, artist.name AS artist_name FROM album JOIN user_album_stats ON album.id=user_album_stats.album_id JOIN artist ON album.artist_id=artist.id GROUP BY id ORDER BY counter DESC LIMIT 10";
        
        $result = $db->fetchAll($query);
        return $result;
    	
    }
    
    function getLatest($limit = 100) {
        
        $db = Zend_Registry::get('database');
        
        $select = $db->select()
                     ->from(array('al' => 'album'), array('album_id' => 'id', 'album_name' => 'name', 'added'))
                     ->join(array('ar' => 'artist'), 'al.artist_id = ar.id', array('artist_id' => 'id', 'artist_name' => 'name'))
                     ->group('al.name')
                     ->order('al.added DESC')
                     ->limit($limit);

        $stmt = $select->query();
        $result = $stmt->fetchAll();
        return $result;
    }

    
    function delete($album_id) {

        $db = Zend_Registry::get('database');

        $n = $db->delete('album', 'id = ' . $album_id);

    }

    function getFavourites($album_id = 0) {
    	
        $db = Zend_Registry::get('database');
        $core   = Zend_Registry::get('core');
    	
        $output = array();
        
        $query = sprintf("SELECT song_id, duration FROM song, user_song_standing WHERE user_song_standing.song_id=song.id AND user_song_standing.user_id=%d AND user_song_standing.standing='love' AND song.album_id=%d", $core->user_id, $album_id);
    	
        $output['items'] = $db->fetchAll($query);
        $output['count'] = count($output['items']);
        
        $duration = 0;
        foreach ($output['items'] as $item) {
        	$duration += $item['duration'];
        }
        $output['cost'] = round($duration / 60); 
        
        return $output;
                
    }
    
}

