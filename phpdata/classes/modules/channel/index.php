<?php


    if ($_GET['mode'] == 'change') {
        
        $new_channel = Channel::getById($_GET['cid']);
        if (count($new_channel) > 0) {
            $core->channel_id = $new_channel['id'];
            $_SESSION['channel_id'] = $core->channel_id;
        }
    
    }
?>