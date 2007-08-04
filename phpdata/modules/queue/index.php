<?php


switch ($_GET['action']) {
    case "addsong":
        Queue::addSong($_GET['param']);
    break;
    case "addalbum":
        Queue::addAlbum($_GET['param']);
    break;

}

$core->template = "queue.tpl";

?>