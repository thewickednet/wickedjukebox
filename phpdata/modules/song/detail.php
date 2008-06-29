<?php


$song = Song::get($_GET['param']);

$artist = Artist::getById($song['artist_id']);
$album = Album::getById($song['album_id']);

$genres = Song::getGenre($_GET['param']);

$channel_data = Song::getChannelData($_GET['param']);

$hate_count = Song::getStandingCount("hate", $_GET['param']);
$love_count = Song::getStandingCount("love", $_GET['param']);

$smarty->assign("CHANNEL_DATA", $channel_data);
$smarty->assign("GENRES", $genres);
$smarty->assign("SONG", $song);
$smarty->assign("ARTIST", $artist);
$smarty->assign("ALBUM", $album);
$smarty->assign("HATES", $hate_count[0]);
$smarty->assign("LOVES", $love_count[0]);

$body_template = "song/detail.tpl";

?>
