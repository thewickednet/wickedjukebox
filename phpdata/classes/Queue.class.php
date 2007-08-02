<?php

class Queue {


    function getCurrent() {
        
        $core   = Zend_Registry::get('core');
        $db     = Zend_Registry::get('database');
        
        $select = $db->select()
                     ->from(array('q' => 'queue'))
                     ->join(array('s' => 'song'), 'q.song_id = s.id')
                     ->join(array('a' => 'artist'), 's.artist_id = a.id')
                     ->join(array('u' => 'users'), 'q.user_id = u.id')
                     ->where('q.channel_id = ?', $core->channel_id)
                     ->order('position');
                     
                     
        $stmt = $select->query();
        $result = $stmt->fetchAll();
        return $result;
        
    }



    function addSong($song_id = null) {
        
        
        
    }


    function addAlbum($album_id = null) {
        
        
        
    }


    function removeItem($queue_id = null) {
        
        
    }


    private function lastPosition() {
        
        
        
        
        
    }







}



?>