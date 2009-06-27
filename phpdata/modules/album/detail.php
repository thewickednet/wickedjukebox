<?php


$album = Album::getById($_GET['param']);

if (isset($_GET['standing']) && $_GET['target'] > 0) {

	$songs = Album::getSongs($_GET['target']);

	foreach ($songs as $song) {
    	User::setStanding($song['id'], $_GET['standing']);
	}
	
	$ajax = true;
}

$songs = Album::getSongs($_GET['param']);
$artist = Artist::getById($album['artist_id']);

for ($i = 0; $i < count($songs); $i++) {
    $songs[$i]['cost'] = Song::evaluateCost($songs[$i]['duration']);
    $songs[$i]['orating'] = Song::getOverallRating($songs[$i]['id']);
}

$album['cost'] = Album::getCost($_GET['param']);

$smarty->assign("ALBUM", $album);
$smarty->assign("ARTIST", $artist);
$smarty->assign("SONGS", $songs);

if ($album['type'] == 'ost' || $album['type'] == 'game' || $album['type'] == 'various')
	if ($ajax)
		$core->template = "album/detail_special.tpl";
	else 
		$body_template = "album/detail_special.tpl";
else
	if ($ajax)
		$core->template = "album/detail.tpl";
	else 
		$body_template = "album/detail.tpl";

?>