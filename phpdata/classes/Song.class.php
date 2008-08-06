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
        
        $query = "SELECT s.id,a.name AS artist_name,s.title,b.name AS album_name, duration, a.id AS artist_id, s.id AS song_id, b.id AS album_id FROM song s INNER JOIN album b ON (s.album_id=b.id) INNER JOIN artist a ON (s.artist_id=a.id) ORDER BY rand() LIMIT 0,12";
        
        $stmt = $db->query($query);
        $result = $stmt->fetchAll();
        for ($i = 0; $i < count($result); $i++) {
            $id = $result[$i]['song_id'];
            $result[$i]['standing'] = User::getStanding($id);
        }
        return $result;
        
    }

    function isBroken($song_id) {
        
        $core   = Zend_Registry::get('core');
        $db     = Zend_Registry::get('database');
        
        $query = "UPDATE song SET broken=1 WHERE id = ?";
        
        $db->query($query, array($song_id));
        
    }

    function getTotalCount() {
    	
        $db     = Zend_Registry::get('database');
        
        $query = "SELECT COUNT(*) AS counter FROM song";
        
        $result = $db->fetchOne($query);
        return $result;
    	
    }
    
    function getTotalSize() {
    	
        $db     = Zend_Registry::get('database');
        
        $query = "SELECT SUM(filesize) FROM song";
        
        $result = $db->fetchOne($query);
        return $result;
    	
    }

    function getPlays() {
    	
        $db     = Zend_Registry::get('database');
        
        $query = "SELECT COUNT(*) as counter, song.id AS song_id, artist.*, artist.id AS artist_id, artist.name AS artist_name, song.title AS song_title, album.name AS album_name, album.id AS album_id FROM song JOIN user_song_stats ON song.id=user_song_stats.song_id JOIN artist ON song.artist_id=artist.id JOIN album ON song.album_id=album.id GROUP BY song_id ORDER BY counter DESC LIMIT 10";
        
        $result = $db->fetchAll($query);
        return $result;
    	
    }

    
    /**
     * Retrieves the list of most hated/loved songs, or the count of loves/hates per track
     * @param $standing Either "love" or "hate"
     * @param $songId [optional] the song Id of which to retrieve the love/hate count
     *
     * EXAMPLE
     *    // retrive the top 10 loved songs
     *    $list = Song::getStandingCount("love");
     *
     *    // retrieve the hate count of the song with Id 123
     *    $hates = Song::getStandingCount("hate", 123);
     */
    function getStandingCount($standing = "love") {
        
        $db     = Zend_Registry::get('database');

        if (func_num_args() == 2){
            $songID = "AND song.id=?";
            $data = array( $standing, func_get_arg(1) );
        } else {
            $songID = "";
            $data = array( $standing );
        }

        
        $query = "SELECT COUNT(*) AS counter, song.id AS song_id, song.title AS song_title, artist.id AS artist_id, artist.name AS artist_name FROM user_song_standing JOIN song ON user_song_standing.song_id=song.id JOIN artist ON artist.id=song.artist_id WHERE standing=? $songID GROUP BY song_id ORDER BY counter DESC LIMIT 10";
        
        $result = $db->fetchAll($query, $data);
        return $result;
        
        
    }
    
    function getLatest() {
        
        $db = Zend_Registry::get('database');
        
        $select = $db->select()
                     ->from(array('s' => 'song'), array('song_id' => 'id', 'song_title' => 'title', 'added'))
                     ->join(array('a' => 'artist'), 's.artist_id = a.id', array('artist_id' => 'id', 'artist_name' => 'name'))
                     ->group('s.title')
                     ->order('s.added DESC')
                     ->limit('100');

        $stmt = $select->query();
        $result = $stmt->fetchAll();
        return $result;
    }

    function delete($song_id) {
        
        $db = Zend_Registry::get('database');
        
        $n = $db->delete('song', 'id = ' . $song_id);
        
    }
    

}



?>
