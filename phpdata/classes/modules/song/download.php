<?php


$song = Song::get($_GET['param']);

$artist = Artist::getById($song['artist_id']);

$filename = sprintf("%02d - %s - %s.mp3", $song['track_no'], $artist['name'], $song['title']);

header("Cache-Control: public, must-revalidate");
header("Pragma: hack"); // WTF? oh well, it works...
header("Content-Type: application/octet-stream");
header("Content-Length: " .(string)(filesize($song['localpath'])) );
header('Content-Disposition: attachment; filename="'.$filename.'"');
header("Content-Transfer-Encoding: binary\n");


readfile(utf8_encode($song['localpath']));

exit();

?>
