<?php



$album = Album::getById($_GET['param']);

$songs = Album::getSongs($_GET['param']);

$artist = Artist::getById($album['artist_id']);

$smarty->assign("ALBUM", $album);
$smarty->assign("ARTIST", $artist);
$smarty->assign("SONGS", $songs);
$body_template = "album/detail.tpl";

?>