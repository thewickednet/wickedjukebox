<?php

class Queue {


    function get($queue_id = null) {
        if (!isset($queue_id))
            return array();


        $db = Zend_Registry::get('database');
        
        $select = $db->select()
                     ->from('queue')
                     ->where('id = ?', $queue_id);
                     
        $stmt = $select->query();
        $result = $stmt->fetchAll();
        if (count($result) == 1)
            return $result[0];
        return array();
    }


    function getCurrent() {
        
        $core   = Zend_Registry::get('core');
        $db     = Zend_Registry::get('database');
        
        $select = $db->select()
                     ->from(array('q' => 'queue'), array('queue_id' => 'id'))
                     ->join(array('s' => 'song'), 'q.song_id = s.id')
                     ->join(array('a' => 'artist'), 's.artist_id = a.id')
                     ->join(array('u' => 'users'), 'q.user_id = u.id')
                     ->where('q.channel_id = ?', $core->channel_id)
                     ->order('position');
                     
                     
        $stmt = $select->query();
        $result = $stmt->fetchAll();
        return $result;
        
    }

    function getTotalTime() {
        
        $core   = Zend_Registry::get('core');
        $db     = Zend_Registry::get('database');
        
        $select = $db->select()
                     ->from(array('q' => 'queue'), array('channel_id'))
                     ->join(array('s' => 'song'), 'q.song_id = s.id', array('totaltime' => 'SUM(duration)'))
                     ->where('q.channel_id = ?', $core->channel_id)
                     ->group('q.channel_id');
                     
        $stmt = $select->query();
        $result = $stmt->fetchAll();
        return $result[0];
        
    }



    function addSong($song_id = null, $position = 0) {
        if (!isset($song_id) || count(Song::get($song_id)) == 0)
            return false;        
            
        if ($position == 0)
            $position = self::lastPosition()+1;

        $core   = Zend_Registry::get('core');
        $db     = Zend_Registry::get('database');

        $data = array(
            'added'         => new Zend_Db_Expr('NOW()'),
            'song_id'       => $song_id,
            'user_id'       => $core->user_id,
            'channel_id'    => $core->channel_id,
            'position'      => $position
        );
        
        $db->insert('queue', $data);        

    }


    function addAlbum($album_id = null) {
        
        $songs = Album::getSongs($album_id);
        
        if (count($songs) > 0) {
            $position = self::lastPosition()+1;
            foreach ($songs as $song) {
                self::addSong($song['id'], $position);
                $position++;
            }
        }
        
    }


    function removeItem($queue_id = null) {
        
        $db     = Zend_Registry::get('database');
        
        $queue_item = self::get($queue_id);
        
        $where  = sprintf("channel_id = %d AND position = %d", $queue_item['channel_id'], $queue_item['position']);
        
        $n = $db->delete('queue', $where);
        if ($n == 1)
            self::shiftAfter($queue_item['position']);
    }


    function clear() {
        
        $core   = Zend_Registry::get('core');
        $db     = Zend_Registry::get('database');
        
        $where  = sprintf("channel_id = %d", $core->channel_id);
        
        $n = $db->delete('queue', $where);

    }


    private function lastPosition() {
        
        $core   = Zend_Registry::get('core');
        $db     = Zend_Registry::get('database');
        
        $select = $db->select()
                     ->from('queue')
                     ->where('channel_id = ?', $core->channel_id)
                     ->order('position DESC')
                     ->limit(1);
                     
        $stmt = $select->query();
        $result = $stmt->fetchAll();
        return $result[0]['position'];
        
    }


    private function shiftAfter($position = 0) {
        
        $core   = Zend_Registry::get('core');
        $db     = Zend_Registry::get('database');
        
        $query = "UPDATE queue SET position=position-1 WHERE channel_id = ? AND position > ?";
        
        $db->query($query, array($core->channel_id, $position));
        
    }


}



?>