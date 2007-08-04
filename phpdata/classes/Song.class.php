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




}



?>