<?php

class Channel {


    function getList() {
        
        $db = Zend_Registry::get('database');
        
        $select = $db->select()
                     ->from('channel')
                     ->order('name');
                     
        $stmt = $select->query();
        $result = $stmt->fetchAll();
        return $result;
        
    }


    function getByName($channel_name = null) {
        
        if (!isset($channel_name) || empty($channel_name))
            return array();
        
        $db = Zend_Registry::get('database');
        
        $select = $db->select()
                     ->from('channel')
                     ->where('name = ?', $channel_name);
                     
        $stmt = $select->query();
        $result = $stmt->fetchAll();
        return $result[0];
    }
    
    function getById($channel_id = null) {
        
        if (!isset($channel_id) || empty($channel_id))
            return array();
        
        $db = Zend_Registry::get('database');
        
        $select = $db->select()
                     ->from('channel')
                     ->where('id = ?', $channel_id);
                     
        $stmt = $select->query();
        $result = $stmt->fetchAll();
        return $result[0];
    }
    
}



?>