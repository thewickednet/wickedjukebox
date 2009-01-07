<?php

    if ($_GET['action'] == 'shout' && $_GET['body'] != '')
        Shoutbox::add($_GET['body']);

    $messages = Shoutbox::getLast();
    
    $now = time() - 480;
    
    for ($i = 0; $i < count($messages); $i++) {
        $temp = strtotime($messages[$i]['shout_added']);
        $messages[$i]['age'] = $now - $temp;
        $messages[$i]['message'] = Core::url2link($messages[$i]['message']);
    }


    $smarty->assign("SHOUTBOX", $messages);

    $core->template = "shoutbox/messages.tpl";

?>