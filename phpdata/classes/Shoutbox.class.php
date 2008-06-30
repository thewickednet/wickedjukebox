<?php


class Shoutbox {


    function getLast() {

        $db = Zend_Registry::get('database');
        
        $select = $db->select()
                     ->from(array('s' => 'shoutbox'), array('message', 'shout_added' => 'added',
                                                            'color' => new Zend_Db_Expr('least(1800, time_to_sec(timediff(NOW(), s.added)))/1800*200')
                     ))
                     ->join(array('u' => 'users'), 's.user_id = u.id')
                     ->order('s.added DESC')
                     ->limit(15);
                     
        $stmt = $select->query();
        $result = $stmt->fetchAll();
        return $result;
    }


    

    function add($message = "") {
            
        $core   = Zend_Registry::get('core');
        $db     = Zend_Registry::get('database');

        $data = array(
            'added'         => new Zend_Db_Expr('NOW()'),
            'user_id'       => $core->user_id,
            'message'       => $message
        );
        
        $db->insert('shoutbox', $data);

    }

    
}









?>
