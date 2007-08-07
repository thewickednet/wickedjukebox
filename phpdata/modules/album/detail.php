<?php



$artist = Artist::getById($_GET['param']);

$songs = Artist::getSongs($_GET['param']);

$smarty->assign("SONGS", $songs);
$smarty->assign("ARTIST", $artist);
$body_template = "artist/detail.tpl";

?>