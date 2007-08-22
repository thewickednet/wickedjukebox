<?php


$song = Song::get($_GET['param']);

$artist = Artist::getById($song['artist_id']);
$album = Album::getById($song['album_id']);

$genres = Song::getGenre($_GET['param']);

$channel_data = Song::getChannelData($_GET['param']);

$smarty->assign("CHANNEL_DATA", $channel_data);
$smarty->assign("GENRES", $genres);
$smarty->assign("SONG", $song);
$smarty->assign("ARTIST", $artist);
$smarty->assign("ALBUM", $album);

$body_template = "song/detail.tpl";

?>