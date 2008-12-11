<?php

$song = Song::get($_GET['param']);

if (isset($_GET['standing'])) {
	$_GET['song'] = $_GET['param'];
	include "report.php";
	$ajax = true;
}


$standing = User::getStanding($_GET['param']);

$artist = Artist::getById($song['artist_id']);
$album = Album::getById($song['album_id']);

$genres = Song::getGenre($_GET['param']);

$channel_data = Song::getChannelData($_GET['param']);

$user_song_standing = User::getStanding($_GET['param']);

$loves = Song::getStandings('love', $_GET['param']);
$hates = Song::getStandings('hate', $_GET['param']);

$smarty->assign("CHANNEL_DATA", $channel_data);
$smarty->assign("USER_STANDING", $user_song_standing);
$smarty->assign("GENRES", $genres);
$smarty->assign("SONG", $song);
$smarty->assign("ARTIST", $artist);
$smarty->assign("STANDING", $standing);
$smarty->assign("ALBUM", $album);
$smarty->assign("HATES", $hates);
$smarty->assign("LOVES", $loves);
$smarty->assign("HATES_COUNT", count($hates));
$smarty->assign("LOVES_COUNT", count($loves));

if ($ajax)
	$core->template = "song/detail.tpl";
else
	$body_template = "song/detail.tpl";

?>