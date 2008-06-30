<?php

    if ($core->user_id == -1)
        $core->template = 'login.tpl';
    else {
        $core->template = 'profile.tpl';
        
        if ($_GET['standing'] == "broken") {
            
            Song::isBroken($_GET['song']);

        } else {
            
            User::setStanding($_GET['song'], $_GET['standing']);
            
        }
    
    }

?>