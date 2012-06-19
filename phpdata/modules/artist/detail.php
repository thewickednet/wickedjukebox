<?php

$artist = Artist::getById($_GET['param']);

$artist['love'] = Artist::getFavourites($_GET['param']);

$cache_key = sprintf("detail_artist_%s_%s", $_GET['param'], $core->user_id);

if (isset($_GET['standing']) && $_GET['target'] > 0 && $_GET['mode'] == 'album') {

	$songs = Album::getSongs($_GET['target']);

	foreach ($songs as $song) {
    	User::setStanding($song['id'], $_GET['standing']);
	}
	unset($songs);
	$ajax = true;
}


if (isset($_GET['standing']) && $_GET['mode'] == 'artist') {

	$cache->remove($cache_key);
	
	$songs = Artist::getSongs($_GET['param']);
	
	foreach ($songs as $song) {
    	User::setStanding($song['song_id'], $_GET['standing']);
	}
	
	$ajax = true;
}

// FIXME: caching doesn't work like it's supposed to
//if(!$songs = $cache->load($cache_key)) {
    
    $albums = Artist::getAlbums($_GET['param']);
    //$songs = Artist::getSingleSongs($_GET['param']);
    //array_push($albums, $songs);

    for ($j = 0; $j < count($albums); $j++) {
		$albums[$j]['songs'] = Album::getSongs($albums[$j]['id']);
		$albums[$j]['love'] = Album::getFavourites($albums[$j]['id']);
		for ($i = 0; $i < count($albums[$j]['songs']); $i++) {
	        $albums[$j]['songs'][$i]['cost'] = Song::evaluateCost($albums[$j]['songs'][$i]['duration']);
	        $albums[$j]['songs'][$i]['orating'] = Song::getOverallRating($albums[$j]['songs'][$i]['id']);
           $albums[$j]['songs'][$i]['prating'] = Song::getCurrentRating($albums[$j]['songs'][$i]['id'], true );
	        $albums[$j]['songs'][$i]['num_loves'] = Song::getStandingCount( "love", $albums[$j]['songs'][$i]['id']);
	        $albums[$j]['songs'][$i]['num_hates'] = Song::getStandingCount( "hate", $albums[$j]['songs'][$i]['id']);
	        
	    }
    }

    $cache->save($albums, $cache_key);
//}



$smarty->assign("RESULT_COUNT", count($albums));
$smarty->assign("ALBUMS", $albums);
$smarty->assign("ARTIST", $artist);

if ($ajax)
	$core->template = 'artist/detail.tpl';
else
	$body_template = "artist/detail.tpl";

