<?php


class BackendDB {
    
    
    function getState($channel_id = null) {
        if (!isset($channel_id))
            return array();

        $db = Zend_Registry::get('database');
        
        $select = $db->select()
                     ->from('state')
                     ->where('channel_id = ?', $channel_id);
                     
        $stmt = $select->query();
        $result = $stmt->fetchAll();
        
        $state = array();

        foreach ($result as $item) {
            $state[$item['state']] = $item['value'];
        }

        return $state;
    }

    function getCurrentSong($channel_id = null) {

        if (!isset($channel_id))
            return array();

        $state = self::getState($channel_id);

        if (empty($state['current_song']))
            return array();

        $songinfo = Song::get($state['current_song']);
        $artistinfo = Artist::getById($songinfo['artist_id']);
        $albuminfo = Album::getById($songinfo['album_id']);

        $result = array(
                        'songinfo'      =>  $songinfo,
                        'userinfo'      =>  $userinfo,
                        'artistinfo'    =>  $artistinfo,
                        'albuminfo'     =>  $albuminfo
                        );

        return $result;

    }

    function playerControl($action = '', $channel_id = null) {

        $core   = Zend_Registry::get('core');
        $xmlrpc = Zend_Registry::get('xmlrpc');

        if (!isset($channel_id))
            $channel_id = $core->channel_id;

        $default_params = array($channel_id);

        switch ($action) {
            case "next":
                $xml_request = "next";
                $params = $default_params;
            break;
            case "play":
                $xml_request = "play";
                $params = $default_params;
            break;
            case "stop":
                $xml_request = "stop";
                $params = $default_params;
            break;
            case "pause":
                $xml_request = "pause";
                $params = $default_params;
            break;
            default:
                return false;            
        }
            
        $xmlrpc_result = $xmlrpc->call($xml_request, $params);
        
        return $xmlrpc_result;
        
    }
    
    
    
}



?>
