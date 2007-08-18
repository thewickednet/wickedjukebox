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





}



?>
