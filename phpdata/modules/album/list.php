<?php


if (empty($_GET['param'])) 
    $_GET['param'] = "a";

$albums = Album::getByAlpha($_GET['param']);


$smarty->assign("ALBUMS", $albums);
$body_template = "album/list.tpl";

?>