<?php



$album = Album::getById($_GET['param']);

$songs = Album::getSongs($_GET['param']);

$artist = Artist::getById($album['artist_id']);

for ($i = 0; $i < count($songs); $i++) {
    $songs[$i]['cost'] = Song::evaluateCost($songs[$i]['duration']);
}

$album['cost'] = Album::getCost($_GET['param']);

$smarty->assign("ALBUM", $album);
$smarty->assign("ARTIST", $artist);
$smarty->assign("SONGS", $songs);

if ($album['type'] == 'ost' || $album['type'] == 'game' || $album['type'] == 'various')
    $body_template = "album/detail_special.tpl";
else
    $body_template = "album/detail.tpl";

?>