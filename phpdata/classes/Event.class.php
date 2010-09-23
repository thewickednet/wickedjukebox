<?php 



class Event {
	
	
    function getById($event_id = null) {
        
        $db = Zend_Registry::get('database');
        
        $select = $db->select()
                     ->from('events')
                     ->where('id = ?', $event_id);
                     
        $stmt = $select->query();
        $result = $stmt->fetchAll();
        return $result[0];
    }
	
	function getUpcoming() {
		
        $db = Zend_Registry::get('database');
        $core   = Zend_Registry::get('core');
    	
        $output = array();
        
        $query = "SELECT * FROM events WHERE TO_DAYS(startdate) > TO_DAYS(NOW())";
    	
        $results = $db->fetchAll($query);
        
        return $results;

	}
	
	
	function getPast() {
		
        $db = Zend_Registry::get('database');
        $core   = Zend_Registry::get('core');
    	
        $output = array();
        
        $query = "SELECT events.*, count(*) AS songs FROM events, user_song_stats WHERE user_song_stats.when>=events.startdate AND user_song_stats.when<=events.enddate GROUP BY events.id ORDER BY startdate DESC";
    	
        $results = $db->fetchAll($query);
        
        return $results;

	}
	
	

    function getPicture($event_id = null) {
        
        if (!isset($event_id) || empty($event_id))
            return array();

        $path = sprintf("%s/../../httpd_data/events/%d.jpg", dirname(__FILE__), $event_id);
        
        return $path;
        
    }
	
    
    function getSongs($event_id = 0) {
    	
        $db = Zend_Registry::get('database');
        $core   = Zend_Registry::get('core');
    	
        $output = array();
        
        $query = sprintf("SELECT user_song_stats.song_id, song.title AS song_title, artist.name AS artist_name, artist.id AS artist_id, count(*) AS played FROM events, user_song_stats, song, artist WHERE song.artist_id=artist.id AND song.id=user_song_stats.song_id AND user_song_stats.when>=events.startdate AND user_song_stats.when<=events.enddate AND events.id=%d GROUP BY song_id ORDER BY played DESC LIMIT 25", $event_id);
    	
        $results = $db->fetchAll($query);
        
        return $results;
    	
    	
    }
	
    function getUsers($event_id = 0) {
    	
        $db = Zend_Registry::get('database');
        $core   = Zend_Registry::get('core');
    	
        $output = array();
        
        $query = sprintf("SELECT user_song_stats.user_id, users.*, COUNT(*) as songs FROM users, user_song_stats, events WHERE user_song_stats.user_id = users.id AND user_song_stats.when>=events.startdate AND user_song_stats.when<=events.enddate AND events.id=%d GROUP BY users.id ORDER BY songs DESC LIMIT 50", $event_id);
    	
        $results = $db->fetchAll($query);
        
        return $results;
    	
    	
    }
	
    
}
