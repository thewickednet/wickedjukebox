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
$body_template = "album/detail.tpl";

?>