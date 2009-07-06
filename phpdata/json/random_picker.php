<?php

$songs = Song::getRandom();

$smarty->assign("RANDOM_SONGS", $songs);

$core->template = "random_picker.tpl";

?>