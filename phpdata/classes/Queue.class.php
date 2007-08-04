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
        if (!isset($song_id) || count(Song::get($song_id)) == 0)
            return false;        

        $core   = Zend_Registry::get('core');
        $db     = Zend_Registry::get('database');

        $data = array(
            'added'         => new Zend_Db_Expr('NOW()'),
            'song_id'       => $song_id,
            'user_id'       => $core->user_id,
            'channel_id'    => $core->channel_id,
            'position'      => self::lastPosition()+1
        );
        
        $db->insert('queue', $data);        

    }


    function addAlbum($album_id = null) {
        
        
        
    }


    function removeItem($queue_id = null) {
        
        
    }


    private function lastPosition() {
        
        $db     = Zend_Registry::get('database');
        
        $select = $db->select('position')
                     ->from('queue')
                     ->where('channel_id = ?', $core->channel_id)
                     ->order('position DESC')
                     ->limit(1);
                     
        $stmt = $select->query();
        $result = $stmt->fetchAll();
        return $result[0]['position'];
        
    }







}



?>