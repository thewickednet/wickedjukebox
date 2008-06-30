<?php

class Auth {
    
    function newCookie($user_id = null) {
        if (!isset($user_id) || empty($user_id))
            return false;
        
        $db = Zend_Registry::get('database');
        
        $cookie = md5(time() * $user_id);
        $data = array(
            'cookie'        => $cookie
        );

        $n = $db->update('users', $data, 'id = ' . $user_id);
        return $cookie;
    }


    function delCookie($user_id = null) {

        if (!isset($user_id) || empty($user_id))
            return false;
        
        $db = Zend_Registry::get('database');

        $data = array(
            'cookie'        => md5(time() * $user_id)
        );

        $n = $db->update('users', $data, 'id = ' . $user_id);
        return $n;
    }


    function getByUsername($username = null) {
        
        if (!isset($username) || empty($username))
            return array();
        
        $db = Zend_Registry::get('database');
        
        $select = $db->select()
                     ->from('users')
                     ->where('username = ?', $username);
                     
        $stmt = $select->query();
        $result = $stmt->fetchAll();
        if (count($result) == 1)
            return $result[0];
        return array();
        
    }

    private function getByCookie($cookie = null) {
        
        if (!isset($cookie) || empty($cookie))
            return array();
        
        $db = Zend_Registry::get('database');
        
        $select = $db->select()
                     ->from('users')
                     ->where('cookie = ?', $cookie);
                     
        $stmt = $select->query();
        $result = $stmt->fetchAll();
        return $result;
        
    }

    function isAuthed() {
        if (isset($_SESSION['wjukebox_auth'])) {
            $cookie = self::getByCookie($_SESSION['wjukebox_auth']);
            if (count($cookie) == 1)
                return true;
        }
        return false;
    }

    function getAuth() {
        if (isset($_SESSION['wjukebox_auth'])) {
            $cookie = self::getByCookie($_SESSION['wjukebox_auth']);
            if (count($cookie) == 1)
                return $cookie[0]['id'];
        }
        return -1;
    }


}


?>