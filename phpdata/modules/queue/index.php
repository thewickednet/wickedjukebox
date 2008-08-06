<?php

switch ($_GET['action']) {
    case "clear":
        if ($core->permissions['queue_remove'] == 1)
            Queue::clear();
    break;
    case "remove":
        if ($core->permissions['queue_remove'] == 1 || Queue::getOwner($_GET['param']) == $core->user_id)
            Queue::removeItem($_GET['param']);
    break;
    case "addsong":
        $cost = Song::getCost($_GET['param']);
        if ($cost <= $core->userdata['credits'] || $core->permissions['nocredits'] == 1) {
            
            if ($core->permissions['nocredits'] == 0)
                User::pay($cost);

            User::addSelect();
            User::hasQueuedSong($_GET['param']);
            Queue::addSong($_GET['param']);
            $smarty->assign("MESSAGE", "UPDATE_PROFILE");
        } else {
            $smarty->assign("MESSAGE", sprintf("Not enough credits!\n %s required, you only have %s.\nJust have a beer and try again in a few minutes, cheers!", $cost, $core->userdata['credits']));
        }
    break;
    case "resort":
        Queue::resort($_POST['queue_list']);
    break;
    case "addalbum":
        $cost = Album::getCost($_GET['param']);
        if ($cost <= $core->userdata['credits'] || $core->permissions['nocredits'] == 1) {
            
            if ($core->permissions['nocredits'] == 0)
                User::pay($cost);
            
            $tracks = Album::getSongs($_GET['param']);
            User::hasQueuedAlbum($_GET['param']);
            User::addSelect(count($tracks));
            Queue::addAlbum($_GET['param']);
            $smarty->assign("MESSAGE", "UPDATE_PROFILE");
        } else {
            $smarty->assign("MESSAGE", sprintf("Not enough credits!\n %s required, you only have %s.\nJust have a beer and try again in a few minutes, cheers!", $cost, $core->userdata['credits']));
        }
    break;
}

if ($_GET['mode'] == 'splash')
  $core->template = "splash/queue.tpl";
else 
  $core->template = "queue.tpl";

?>