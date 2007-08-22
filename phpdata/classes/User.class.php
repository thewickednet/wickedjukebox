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


}



?>
