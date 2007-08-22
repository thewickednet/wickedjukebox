<?php

$songs = Song::getRandom();


    for ($i = 0; $i < count($songs); $i++) {
        $songs[$i]['cost'] = Song::evaluateCost($songs[$i]['duration']);
    }


$smarty->assign("RANDOM_SONGS", $songs);

$core->template = "song/random.tpl";

?>