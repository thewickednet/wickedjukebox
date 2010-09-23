<?php


switch ($_GET['action']) {
    case "next":
        Backend::playerControl('next', 1);
    break;
    case "stop":
        Backend::playerControl('stop', 1);
    break;
    case "pause":
        Backend::playerControl('pause', 1);
    break;
    case "play":
        Backend::playerControl('play', 1);
    break;

}

$core->template = "queue.tpl";

