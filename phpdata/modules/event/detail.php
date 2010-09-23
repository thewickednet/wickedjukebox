<?php 

$event = Event::getById($_GET['param']);

$songs = Event::getSongs($_GET['param']);
$users = Event::getUsers($_GET['param']);

$smarty->assign("EVENT", $event);

$smarty->assign("SONGS", $songs);
$smarty->assign("SONG_COUNT", count($songs));

$smarty->assign("USERS", $users);
$smarty->assign("USER_COUNT", count($users));

$body_template = 'event/detail.tpl';