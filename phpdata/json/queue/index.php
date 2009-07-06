<?php 

$success = 0;
$message = "unknown";

switch ($_GET['action']) {
    case "clear":
        if ($core->permissions['queue_remove'] == 1)
            Queue::clear();
    break;
    case "remove":
    	$queue_item = Queue::get($_GET['param']);
        if ($core->permissions['queue_remove'] == 1 || $queue_item['user_id'] == $core->user_id) {
            if ($queue_item['user_id'] == $core->user_id) {
        		$cost = Song::getCost($queue_item['song_id']);
            	User::pay($cost * -1);
            }
        	Queue::removeItem($_GET['param']);
        }
    break;
    case "addsong":
        $cost = Song::getCost($_GET['param']);
        if ($cost <= $core->userdata['credits'] || $core->permissions['nocredits'] == 1) {
            
            if ($core->permissions['nocredits'] == 0)
                User::pay($cost);

            User::addSelect();
            User::hasQueuedSong($_GET['param']);
            Queue::addSong($_GET['param']);
            $success = 1;            
        	$message = "DONE";
        } else {
        	$message = "NO_CREDITS";
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
			
            $success = 1;            
            $tracks = Album::getSongs($_GET['param']);
            User::hasQueuedAlbum($_GET['param']);
            User::addSelect(count($tracks));
            Queue::addAlbum($_GET['param']);
            $smarty->assign("MESSAGE", "UPDATE_PROFILE");
        	$message = "DONE";
        } else {
        	$message = "NO_CREDITS";
        }
    break;
}

$smarty->assign("MESSAGE", $message);
$smarty->assign("SUCCESS", $success);
$core->template = "simple_action.tpl";

?>