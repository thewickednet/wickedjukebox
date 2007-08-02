<?php


if (empty($_GET['param'])) 
    $_GET['param'] = "a";

$artists = Artist::getByAlpha($_GET['param']);


$smarty->assign("ARTISTS", $artists);
$body_template = "artist/list.tpl";

?>