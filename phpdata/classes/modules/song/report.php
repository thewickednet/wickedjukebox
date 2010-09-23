<?php

    if ($core->user_id == -1)
        $core->template = 'login.tpl';
    else {
        $core->template = 'profile.tpl';

        if ($_GET['standing'] == "broken") {

            Song::isBroken($_GET['song']);

        } else {

			$cache_key = sprintf("detail_artist_%s_%s", $_GET['song'], $core->user_id);
        	$cache->remove($cache_key);

        	$cache_key = sprintf("favorites_%d", $core->user_id);
            $cache->remove($cache_key);

            User::setStanding($_GET['song'], $_GET['standing']);

        }
    
    }

?>