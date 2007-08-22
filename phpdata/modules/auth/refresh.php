<?php

    if ($core->user_id == -1)
        $core->template = 'login.tpl';
    else 
        $core->template = 'profile.tpl';
    
?>