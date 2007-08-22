<?php

class Song {



    function get($song_id = null) {
        if (!isset($song_id))
            return array();


        $db = Zend_Registry::get('database');
        
        $select = $db->select()
                     ->from('song')
                     ->where('id = ?', $song_id);
                     
        $stmt = $select->query();
        $result = $stmt->fetchAll();
        if (count($result) == 1)
            return $result[0];
        return array();
    }

    function getCost($song_id = null) {
        if (!isset($song_id))
            return array();


        $db = Zend_Registry::get('database');
        
        $select = $db->select()
                     ->from('song')
                     ->where('id = ?', $song_id);
                     
        $stmt = $select->query();
        $result = $stmt->fetchAll();
        if (count($result) == 1)
            return round($result[0]['duration']/60);
        return 0;
    }

    function evaluateCost($duration, $song_id = null) {

        $cost = 0;

        if (isset($song_id)) {
            
        $db = Zend_Registry::get('database');
        
        $select = $db->select()
                     ->from('song')
                     ->where('id = ?', $song_id);
            
            
        } else {
            
            $cost = round($duration/60);
            
        }
        if ($cost == 0)
            $cost = 1;

        return $cost;
    
    
    }

    function getChannelData($song_id = null) {
        if (!isset($song_id))
            return array();

        $core   = Zend_Registry::get('core');
        $db     = Zend_Registry::get('database');
        
        $select = $db->select()
                     ->from('channel_song_data')
                     ->where('channel_id = ?', $core->channel_id)
                     ->where('song_id = ?', $song_id);
                     
        $stmt = $select->query();
        $result = $stmt->fetchAll();
        if (count($result) == 1)
            return $result[0];
        return array();
    }

    function getGenre($song_id) {
        
        $db = Zend_Registry::get('database');
        
        $select = $db->select()
                     ->distinct()
                     ->from(array('a' => 'genre'))
                     ->join(array('h' => 'song_has_genre'), 'h.genre_id = a.id')
                     ->where('song_id = ?', $song_id);

        $stmt = $select->query();
        $result = $stmt->fetchAll();
        return $result;
    }

    
    
    function getRandom() {
        
        $core   = Zend_Registry::get('core');
        $db     = Zend_Registry::get('database');
        
        $query = "SELECT s.id,a.name AS artist_name,s.title,b.name AS album_name, duration, a.id AS artist_id, s.id AS song_id, b.id AS album_id FROM song s INNER JOIN album b ON (s.album_id=b.id) INNER JOIN artist a ON (s.artist_id=a.id) ORDER BY rand() LIMIT 0,10";
        
        $stmt = $db->query($query);
        $result = $stmt->fetchAll();
        return $result;
        
    }


}



?>