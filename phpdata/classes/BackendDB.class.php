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

        $standings['love'] = Song::getStandings('love', $state['current_song']);
        $standings['hate'] = Song::getStandings('hate', $state['current_song']);

        $standings['love_count'] = count($standings['love']);
        $standings['hate_count'] = count($standings['hate']);

        if ($state['upcoming_song'] > 0) {
        $next_songinfo = Song::get($state['upcoming_song']);
        $next_artistinfo = Artist::getById($next_songinfo['artist_id']);
        $next_albuminfo = Album::getById($next_songinfo['album_id']);
        } else
                $nextinfo = array();

        $progress = $state['progress'];
        $progress = $songinfo['duration'] / 100 * $progress;
        
        $step = 100 / $songinfo['duration'];

        $result = array(
                        'songinfo'      =>  $songinfo,
                        'userinfo'      =>  $userinfo,
                        'artistinfo'    =>  $artistinfo,
                        'albuminfo'     =>  $albuminfo,
                        'standings'     =>  $standings,
                        'state'         =>  $state,
                        'nextsong'	=>  $next_songinfo,
                        'nextartist'	=>  $next_artistinfo,
                        'nextalbum'	=>  $next_albuminfo,
                        'step'          =>  $step,
                        'progress'      =>  $progress
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


    function skip() {

    	$db 	= Zend_Registry::get('database');
    	$core 	= Zend_Registry::get('core');

        $data = array('value' => 1);

        $n = $db->update('state', $data, "state = 'skipping' AND channel_id = " . $core->channel_id);
    }


}


