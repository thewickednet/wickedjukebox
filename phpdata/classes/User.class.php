<?php

class User {


    function getUser($user_id = null) {
        
        if (!isset($user_id) || empty($user_id))
            return array();
        
        $db = Zend_Registry::get('database');
        
        $select = $db->select()
                     ->from('users')
                     ->where('id = ?', $user_id);
                     
        $stmt = $select->query();
        $result = $stmt->fetchAll();
        return $result[0];
        
    }

    function getPicture($user_id = null) {
        
        if (!isset($user_id) || empty($user_id))
            return array();
        $user = self::getUser($user_id);

        if ($user['picture'] == '') return "";
        
        $path = sprintf("%s/../../httpd_data/users/%s", dirname(__FILE__), $user['picture']);
        
        return $path;
        
    }

    function getPermissions($group_id = null) {
        
        if (!isset($group_id) || empty($group_id))
            return array();
        
        $db = Zend_Registry::get('database');
        
        $select = $db->select()
                     ->from('groups')
                     ->where('id = ?', $group_id);
                     
        $stmt = $select->query();
        $result = $stmt->fetchAll();
        return $result[0];
        
    }


    function pay($cost) {
        
        $core   = Zend_Registry::get('core');
        $db     = Zend_Registry::get('database');
        $logger = Zend_Registry::get('logger');
        
        $logger->info(sprintf("user %s pays %s credits", $core->user_id, $cost));
        
        $query = sprintf("UPDATE users SET credits=credits-%d WHERE id = ?", $cost);
        
        $db->query($query, array($core->user_id));
        
    }

    function addSelect($counter = 1) {
        
        $core   = Zend_Registry::get('core');
        $db     = Zend_Registry::get('database');
        
        $query = sprintf("UPDATE users SET selects=selects+%d WHERE id = ?", $counter);
        
        $db->query($query, array($core->user_id));
        
    }


    function hasQueuedSong($song_id = null) {
        if (!isset($song_id) || count(Song::get($song_id)) == 0)
            return false;
            
        $core   = Zend_Registry::get('core');
        $db     = Zend_Registry::get('database');

        $data = array(
            'when'          => new Zend_Db_Expr('NOW()'),
            'song_id'       => $song_id,
            'user_id'       => $core->user_id
        );
        
        $db->insert('user_song_stats', $data);        

    }

    function hasQueuedAlbum($album_id = null) {
        if (!isset($album_id) || count(Album::getSongs($album_id)) == 0)
            return false;
            
        $core   = Zend_Registry::get('core');
        $db     = Zend_Registry::get('database');

        $data = array(
            'when'          => new Zend_Db_Expr('NOW()'),
            'album_id'       => $album_id,
            'user_id'       => $core->user_id
        );
        
        $db->insert('user_album_stats', $data);        

    }

    function setStanding($song_id = null, $standing = "neutral") {
        if (!isset($song_id) || count(Song::get($song_id)) == 0)
            return false;
            
        $core   = Zend_Registry::get('core');
        $db     = Zend_Registry::get('database');


        if ($standing == "neutral")
            $query = "DELETE FROM user_song_standing WHERE user_id=? AND song_id=?";
        else
            $query = sprintf("REPLACE INTO user_song_standing (user_id, song_id, standing) VALUES (?, ?, '%s')", $standing);
        
        
        
        $db->query($query, array($core->user_id, $song_id));

    }

    function getTotalCount() {
    	
        $db     = Zend_Registry::get('database');
        
        $query = "SELECT COUNT(*) AS counter FROM users";
        
        $result = $db->fetchOne($query);
        return $result;
    	
    }
    
    function getActive() {
    	
        $db     = Zend_Registry::get('database');
        
        $query = "SELECT * FROM users WHERE selects > 0 ORDER BY selects DESC LIMIT 10";
        
        $result = $db->fetchAll($query);
        return $result;
    	
    }
    
    function getAlive() {
    	
        $db     = Zend_Registry::get('database');
        
        $query = "SELECT *, UNIX_TIMESTAMP()-UNIX_TIMESTAMP(proof_of_listening) AS listen FROM users WHERE UNIX_TIMESTAMP()-UNIX_TIMESTAMP(proof_of_life) < 180";
        
        $result = $db->fetchAll($query);
        return $result;
    	
    }
    
    function giveProof() {
        
        $core   = Zend_Registry::get('core');
        $db     = Zend_Registry::get('database');

        
        $query = "UPDATE users SET proof_of_life = NOW(), IP = ? WHERE id=?";
        
        $db->query($query, array($_SERVER['REMOTE_ADDR'], $core->user_id));
        
    }
    
    
    function getPlays() {
    	
        $db     = Zend_Registry::get('database');
        
        $query = "SELECT * FROM users ORDER by selects LIMIT 10";
        
        $result = $db->fetchAll($query);
        return $result;
    	
    }

    function getShouts() {
    	
        $db     = Zend_Registry::get('database');
        
        $query = "SELECT DISTINCT COUNT(*) AS counter, users.* FROM shoutbox JOIN users ON users.id=shoutbox.user_id GROUP BY fullname ORDER by counter DESC LIMIT 10";
        
        $result = $db->fetchAll($query);
        return $result;
    	
    } 

    function getDownloads() {
    	
        $db     = Zend_Registry::get('database');
        
        $query = "SELECT * FROM users ORDER by downloads LIMIT 10";
        
        $result = $db->fetchAll($query);
        return $result;
    	
    }

    function getStanding($song_id = null) {
        
        if (!isset($song_id) || count(Song::get($song_id)) == 0)
            return false;
        
        $db     = Zend_Registry::get('database');
        $core   = Zend_Registry::get('core');
        
        $query = "SELECT standing FROM user_song_standing WHERE user_id=? AND song_id=?";
        
        $standing = $db->fetchOne($query, array($core->user_id, $song_id));
        return $standing;
        
    }

    function getStandings($standing = "love") {
        
        $db = Zend_Registry::get('database');
        $core   = Zend_Registry::get('core');
        
        $query = "SELECT standing FROM user_song_standing WHERE user_id=? AND song_id=?";
        
        $standing = $db->fetchOne($query, array($core->user_id, $song_id));
        return $standing;
        
    }

    function getFavorites($user_id = 0, $standing = "love", $limit = 0, $random  = false) {
        
        $db = Zend_Registry::get('database');
        $core   = Zend_Registry::get('core');
        
        $query = "SELECT song.title AS song_title, artist.name AS artist_name, album.name AS album_name, song.id AS song_id, album.id AS album_id, artist.id AS artist_id FROM user_song_standing JOIN song ON user_song_standing.song_id=song.id JOIN artist ON song.artist_id = artist.id JOIN album ON album.id=song.album_id WHERE user_id=? AND standing = ?";

        if ($random)
            $query .= " ORDER BY RAND() ";
        else 
            $query .= "ORDER BY artist_name, song_title";
         
        if ($limit > 0)
            $query .= sprintf(" LIMIT %d", $limit);
        
        $songs = $db->fetchAll($query, array($user_id, $standing));
        return $songs;
        
        
    }
    
    
    function set($data = array(), $user_id = 0) {
        
        if ($user_id == 0) {
            $data['added'] = new Zend_Db_Expr('CURDATE()');
        
            $db->insert('users', $data);
            return $db->lastInsertId();

        } else {

            $db->update('users', $data, 'id = ' . $user_id);
            
        }
        return $user_id;
        
    }

    function getAll() {
        
        $db = Zend_Registry::get('database');

        $select = $db->select()
                     ->from('users')
                     ->order('fullname');
                     
        $stmt = $select->query();
        $result = $stmt->fetchAll();
        return $result;
    }

}


?>