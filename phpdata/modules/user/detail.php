<?php

    $user = User::getUser($_GET['param']);

    $smarty->assign("USER", $user);
    $smarty->assign("GROUP", User::getPermissions($user['group_id']));


    $love = User::getFavorites($_GET['param'], "love", 20, true);
    $hate = User::getFavorites($_GET['param'], "hate", 20, true);
    
    $smarty->assign("LOVE", $love);
    $smarty->assign("HATE", $hate);
    
    $body_template = 'user/detail.tpl';

?>