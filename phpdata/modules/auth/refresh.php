<?php

    if ($core->user_id == -1)
        $core->template = 'login.tpl';
    else {
      if ($_GET['mode'] == 'splash')
        $core->template = 'splash/top.tpl';
      else
        $core->template = 'profile.tpl';
        
    }
    
?>