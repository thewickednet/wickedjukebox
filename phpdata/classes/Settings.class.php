<?
class Settings {


    function getChannelSettings($channel_id = 0, $user_id = 0) {
        
        $db = Zend_Registry::get('database');

        $select = $db->select()
                     ->from(array('s' => 'setting'))
                     ->join(array('t' => 'setting_text'), 's.var = t.var')
                     ->where('channel_id = ?', $channel_id)
                     ->where('user_id = ?', $user_id);
        
        $stmt = $select->query();
        $result = $stmt->fetchAll();
        return $result;
    }

    function getChannelSetting($channel_id = 0, $user_id = 0, $var = '') {
        
        $db = Zend_Registry::get('database');

        $select = $db->select()
                     ->from(array('s' => 'setting'))
                     ->where('channel_id = ?', $channel_id)
                     ->where('user_id = ?', $user_id)
                     ->where('var = ?', $var);
        
        $stmt = $select->query();
        $result = $stmt->fetch();
        return $result;
    }

    function getGlobalSettings() {
        
        $db = Zend_Registry::get('database');

        $select = $db->select()
                     ->from(array('s' => 'setting'))
                     ->join(array('t' => 'setting_text'), 's.var = t.var')
                     ->where('channel_id = 0')
                     ->where('user_id = 0');

        
        $stmt = $select->query();
        $result = $stmt->fetchAll();
        return $result;
    }

    
    function setChannelSettings($channel_id = 0, $user_id = 0, $param = "", $value = "") {
        
        $db = Zend_Registry::get('database');
        
        $where = array();
        $data = array(
            'value'      => $value
        );
        
        $where[] = sprintf("user_id = %d", $user_id);
        $where[] = sprintf("channel_id = %d", $channel_id);
        $where[] = sprintf("var = '%s'", $param);
        
        $n = $db->update('setting', $data, $where);
                
        
    }

    function setGlobalSettings($param = "", $value = "") {

        $db = Zend_Registry::get('database');

        $where = array();
        $data = array(
            'value'      => $value
        );

        $where[] = "channel_id = 0";
        $where[] = "user_id = 0";
        $where[] = sprintf("var = '%s'", $param);

        $n = $db->update('setting', $data, $where);

    }
    
}     
?>