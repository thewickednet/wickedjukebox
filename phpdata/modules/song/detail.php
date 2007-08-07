<?php


$song = Song::get($_GET['param']);

$artist = Artist::getById($song['artist_id']);
$album = Album::getById($song['album_id']);

$smarty->assign("SONG", $song);
$smarty->assign("ARTIST", $artist);
$smarty->assign("ALBUM", $album);

$body_template = "song/detail.tpl";

?>