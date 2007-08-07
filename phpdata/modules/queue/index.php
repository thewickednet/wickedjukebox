<?php


switch ($_GET['action']) {
    case "clear":
        Queue::clear();
    break;
    case "remove":
        Queue::removeItem($_GET['param']);
    break;
    case "addsong":
        Queue::addSong($_GET['param']);
    break;
    case "resort":
        Queue::resort($_POST['queue_list']);
    break;
    case "addalbum":
        Queue::addAlbum($_GET['param']);
    break;

}

$core->template = "queue.tpl";

?>