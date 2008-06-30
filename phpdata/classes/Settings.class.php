<?
class Settings {


    function getChannelSettings($channel_id = 0) {
        
        $db = Zend_Registry::get('database');
        

        $select = $db->select()
                     ->from(array('s' => 'setting'))
                     ->where('channel_id = ?', $channel_id);

        
        $stmt = $select->query();
        $result = $stmt->fetchAll();
        return $result;
    }

    function getGlobalSettings() {
        
        $db = Zend_Registry::get('database');
        

        $select = $db->select()
                     ->from(array('s' => 'setting'))
                     ->where('channel_id = NULL');

        
        $stmt = $select->query();
        $result = $stmt->fetchAll();
        return $result;
    }

    
    function setChannelSettings($channel_id = 0, $param = "", $value = "") {
        
        $db = Zend_Registry::get('database');
        
        $where = array();
        $data = array(
            'value'      => $value
        );
        
        $where[] = sprintf("channel_id = %d", $channel_id);
        $where[] = sprintf("var = '%s', $param");
        
        $n = $db->update('setting', $data, $where);
                
        
    }
    
    
    function setGlobalSettings($param = "", $value = "") {
        
        $db = Zend_Registry::get('database');
        
        $where = array();
        $data = array(
            'value'      => $value
        );
        
        $where[] = "channel_id = NULL";
        $where[] = sprintf("var = '%s', $param");
        
        $n = $db->update('setting', $data, $where);
                
        
    }
    
    
    
    
    
    
}     
?>