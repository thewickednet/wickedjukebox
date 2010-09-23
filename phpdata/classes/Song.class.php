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

    function getHistory() {
        
        $db = Zend_Registry::get('database');
        $core   = Zend_Registry::get('core');
        
            $select = $db->select()
                         ->from(array('h' => 'history'))
                     	 ->where('channel = ?', $core->channel_id)
                     	 ->order('time DESC')
                     	 ->limit(100);
                     	 
		$stmt = $select->query();
        $result = $stmt->fetchAll();
        return $result;
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
    
    function getStandings($standing = "love", $song_id = 0) {
    	
        $db     = Zend_Registry::get('database');

        $select = $db->select()
                     ->from(array('uss' => 'user_song_standing'))
                     ->join(array('u' => 'users'), 'u.id = uss.user_id')
                     ->where('song_id = ?', $song_id)
                     ->where('standing = ?', $standing);
        
        $stmt = $select->query();
        $result = $stmt->fetchAll();
    	  return $result;
    }
    
    /**
     * Count the number of loves/hates for a given song
     *
     * @param $standing: Can either be "love" or "hate"
     * @param $song_id: The song id
     */
    function getCurrentStandingCount($standing = "love", $song_id = 0) {
        $db     = Zend_Registry::get('database');

        /* find out who's listening */
        $select = $db->select()
                     ->from( 'users', array("id") )
                     ->where( 'NOW() - proof_of_listening <= 300' );
        $result = $select->query()->fetchAll();
        $ids = array();
        foreach ( $result as $row ){
            $ids[] = $row['id'];
        }
        if ( count( $ids ) == 0 ){
            return 0;
        }

        $ids = implode( ",", $ids );
        
        /* Count the standings */
        if ($song_id != 0){
          $select = $db->select()
                       ->from('user_song_standing', array('song_id', 'counter' => 'COUNT(*)'))
                       ->group('song_id')
                       ->where('user_id IN ('.$ids.')')
                       ->where('song_id = ?', $song_id)
                       ->where('standing = ?', $standing);
          
          $stmt = $select->query();
          $result = $stmt->fetchAll();
        } else {
          $select = $db->select()
                       ->from(array('uss' => 'user_song_standing'), array('counter' => 'COUNT(*)'))
                       ->join(array('s' => 'song'), 's.id = uss.song_id', array('song_id' => 'id', 'song_title' => 'title'))
                       ->join(array('a' => 'artist'), 's.artist_id = a.id', array('artist_id' => 'id', 'artist_name' => 'name'))
                       ->group('song_id')
                       ->where('uss.user_id IN ('.$ids.')')
                       ->where('standing = ?', $standing)
                       ->order('counter DESC')
        	             ->limit(10);
          $stmt = $select->query();
          $result = $stmt->fetchAll();
        }
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
    function getStandingCount($standing = "love", $song_id = 0) {
        
        $db     = Zend_Registry::get('database');

      if ($song_id != 0){
        $select = $db->select()
                     ->from('user_song_standing', array('song_id', 'counter' => 'COUNT(*)'))
                     ->group('song_id')
                     ->where('song_id = ?', $song_id)
                     ->where('standing = ?', $standing);
        
        $stmt = $select->query();
        $result = $stmt->fetchAll();
      } else {
        $select = $db->select()
                     ->from(array('uss' => 'user_song_standing'), array('counter' => 'COUNT(*)'))
                     ->join(array('s' => 'song'), 's.id = uss.song_id', array('song_id' => 'id', 'song_title' => 'title'))
                     ->join(array('a' => 'artist'), 's.artist_id = a.id', array('artist_id' => 'id', 'artist_name' => 'name'))
                     ->group('song_id')
                     ->where('standing = ?', $standing)
                     ->order('counter DESC')
      	             ->limit(10);
        $stmt = $select->query();
        $result = $stmt->fetchAll();
      }
      return $result;
        
        
    }
    
    function getLyrics($song_id = 0) {
    	
    	$song = self::get($song_id);
    	$artist = Artist::getById($song['artist_id']);
    	$xml_request = sprintf("http://api.chartlyrics.com/apiv1.asmx/SearchLyricDirect?&artist=%s&song=%s", urlencode($artist['name']), urlencode($song['title']));
    	
    	$response = file_get_contents($xml_request);
    	$xml = new SimpleXMLElement($response);
    	
    	$result = $xml->xpath('/GetLyricResult');
                
    	if ($xml->LyricId == 0)
    		return $result->lyrics;
    	else		
    		self::setLyrics($song_id, $xml->Lyric);
    	
    	return ""; 
    	
    }
    
    
    function getLatest($limit = 100) {
        
        $db = Zend_Registry::get('database');
        
        $select = $db->select()
                     ->from(array('s' => 'song'), array('song_id' => 'id', 'song_title' => 'title', 'added'))
                     ->join(array('a' => 'artist'), 's.artist_id = a.id', array('artist_id' => 'id', 'artist_name' => 'name'))
                     ->where('s.album_id = 0')
                     ->group('s.title')
                     ->order('s.added DESC')
                     ->limit($limit);

        $stmt = $select->query();
        $result = $stmt->fetchAll();
        return $result;
    }

    function delete($song_id) {
        
        $db = Zend_Registry::get('database');
        
        $n = $db->delete('song', 'id = ' . $song_id);
        
    }
    
    function setLyrics($song_id = 0, $lyrics = "") {
    	
    	$db = Zend_Registry::get('database');
    	
    	$data = array(
    					'lyrics'      => $lyrics
		);

    	$n = $db->update('song', $data, 'id = ' . $song_id);
    	
    	
    }

    /**
     * Calculate the song rating
     *
     * @param $positive: Count of loves
     * @param $negative: Count of hates
     * @param $parametric: return a parametric instead of an absolute value
     */
    private function calc_rating( $positive, $negative, $parametric=false ){
        if ($parametric) {
            if ( $positive-$negative < 0){ 
               return -($negative / ($positive+$negative));
            } elseif ($positive-$negative > 0 ) {
               return $positive / ($positive+$negative);
            } else {
               return "0.0";
            }
        } else {
            return $positive - $negative;
        }
    }

    /**
     * Retrieve the song rating while counting only listening users
     *
     * @param $song_id: The song ID
     * @type $song: int
     */
    function getCurrentRating( $song_id, $parametric=false ){
    	$positive = self::getCurrentStandingCount('love', $song_id);
    	$negative = self::getCurrentStandingCount('hate', $song_id);
		$positive = $positive[0]['counter'];
		$negative = $negative[0]['counter'];
      return self::calc_rating( $positive, $negative, $parametric );
    }

    function getOverallRating($song_id, $parametric=false) {
    	
    	$positive = self::getStandingCount('love', $song_id);
    	$negative = self::getStandingCount('hate', $song_id);
		$positive = $positive[0]['counter'];
		$negative = $negative[0]['counter'];

      return self::calc_rating( $positive, $negative, $parametric );
    	
    }
    

}


