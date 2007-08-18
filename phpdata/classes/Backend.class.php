<?php


class Backend {
    
    
    function getCurrentSong($channel_id = null) {
        
        $core   = Zend_Registry::get('core');
        $xmlrpc = Zend_Registry::get('xmlrpc');

        
        if (!isset($channel_id))
            $channel_id = $core->channel_id;
        
        $xmlrpc_result = $xmlrpc->call('getCurrentSong', array($channel_id));
        $info = array();
        preg_match('/\{"userid": (.*), "id": (\d+)\}/', $xmlrpc_result, $info);

        if ($info[1] != 'null'){
           $userinfo = User::getUser($info[1]);
        } else {
           $userinfo = array(
              'username' => 'the jukebox'
              );
        }

        $songinfo = Song::get($info[2]);
        $artistinfo = Artist::getById($songinfo['artist_id']);
        $albuminfo = Artist::getById($songinfo['album_id']);
        
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
