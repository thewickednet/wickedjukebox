<?php

class Album {

    function getByAlpha($alpha = "a") {
        
        $db = Zend_Registry::get('database');
        
        $select = $db->select()
                     ->distinct()
                     ->from(array('a' => 'album'), array('album_id' => 'id', 'album_name' => 'name'))
                     ->join(array('ar' => 'artist'), 'a.artist_id = ar.id', array('artist_id' => 'id', 'artist_name' => 'name'))
                     ->join(array('s' => 'song'), 's.album_id = a.id', array('songs' => 'COUNT(*)'))
                     ->where('substr(a.name, 1, 1) = ?', $alpha)
                     ->group('a.name')
                     ->order('a.name');

        $stmt = $select->query();
        $result = $stmt->fetchAll();
        return $result;
    }

    function getSongs($album_id = null) {
        
        $db = Zend_Registry::get('database');
        
        $select = $db->select()
                     ->from(array('s' => 'song'))
                     ->where('s.album_id = ?', $album_id)
                     ->order('track_no', 'title');
                     
        $stmt = $select->query();
        $result = $stmt->fetchAll();
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

    $filemasks = array('folder.jpg', 'Folder.jpg', 'cover.jpg', 'Cover.jpg', 'folder.gif', 'Folder.gif');

    $songs = self::getSongs($album_id);
    foreach($songs as $song) {
      foreach($filemasks as $filemask){
        $check = dirname($song['localpath']) . '/' . $filemask;
        if (file_exists($check))
          return $check;
      }

    }

    return "";

  }

}



?>