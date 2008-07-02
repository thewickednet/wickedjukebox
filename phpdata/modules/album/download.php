<?php



$album = Album::getById($_GET['param']);

$songs = Album::getSongs($_GET['param']);

$artist = Artist::getById($album['artist_id']);

$album_cover = Album::findCover($_GET['param']);
        
$tempname = tempnam("/tmp", "wj");

$filename = sprintf("%s - %s.zip", $artist['name'], $album['name']);

$zip = new ZipArchive();

if ($zip->open($tempname, ZIPARCHIVE::OVERWRITE)!==TRUE) {
    exit("cannot open <$tempname>\n");
}

if ($album_cover != '') {
    $icon_path = sprintf("/%s - %s/folder.jpg", $artist['name'], $album['name']);
    $zip->addFile($album_cover, $icon_path);
}

foreach ($songs as $song) {
    $song_file = sprintf("/%s - %s/%02d - %s.mp3", $artist['name'], $album['name'], $song['track_no'], $song['title']);
    $zip->addFile($song['localpath'], $song_file);
}

$zip->close();

header("Cache-Control: public, must-revalidate");
header("Pragma: hack"); // WTF? oh well, it works...
header("Content-Type: application/octet-stream");
header("Content-Length: " .(string)(filesize($tempname)) );
header('Content-Disposition: attachment; filename="'.$filename.'"');
header("Content-Transfer-Encoding: binary\n");

readfile($tempname);

exit();

?>