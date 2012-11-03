<?php

    
$original = array("&","'",":","/","@","�", "�", "�", "�", "�", "�", " ", ".");
$entities = array("AND","QUOTE","DOUBLES","SLASH","AT","EE", "AE", "UE", "EE", "AA", "OE", "_", "DOT");

$cache_key = str_replace($original, $entities, utf8_decode($search_pattern));
$cache_key = sprintf("%s_%s", $cache_key, $search_mode);

if (strlen($search_pattern) < 3) {

    $smarty->assign("ERROR_MESSAGE", "Search pattern must be at least 3 characters long!");

} elseif (strlen($search_pattern) > 20) {

    $smarty->assign("ERROR_MESSAGE", "Search pattern shouldn't be longer than 20 characters!");

} else {

    //if(!$results = $cache->load($cache_key)) {
    
        switch ($search_mode) {
            case "artist":
                $results = Search::byArtist($search_pattern);
            break;
            case "album":
                $results = Search::byAlbum($search_pattern);
            break;
            case "song":
                $results = Search::bySong($search_pattern);
            break;
            case "lyrics":
                $results = Search::byLyrics($search_pattern);
            break;
            case "any":
            default:
                $results = Search::byAny($search_pattern);
            break;
        }
    
        for ($i = 0; $i < count($results); $i++) {
            $results[$i]['cost'] = Song::evaluateCost($results[$i]['duration']);
            $results[$i]['standing'] = User::getStanding($results[$i]['song_id']);
            $results[$i]['orating'] = Song::getOverallRating($results[$i]['song_id']);
            $results[$i]['prating'] = Song::getCurrentRating($results[$i]['song_id'], true);
            $results[$i]['num_loves'] = Song::getStandingCount("love", $results[$i]['song_id']);
            $results[$i]['num_hates'] = Song::getStandingCount("hate", $results[$i]['song_id']);
        }
    
        //$artists = Artist::getByAlpha($alpha);
        $cache->save($results, $cache_key);
    //}

}


    require_once 'Pager/Pager.php';
    $params = array(
        'mode'      => 'Sliding',
        'perPage'   => 50,
        'delta'     => 8,
        'append'    => false,
        'urlVar'    => 'pagenum',
        'path'      => '',
        'prevImg'   => '<img src="/images/resultset_previous.png" border="0" />',
        'nextImg'   => '<img src="/images/resultset_next.png" border="0" />',
        'fileName'  => "javascript:blaatOverSearch(%d)",
        'itemData'  => $results
    );

    $pager = & Pager::factory($params);
    $data  = $pager->getPageData();
    $links = $pager->getLinks();

    $smarty->assign("LINKS", $links['all']);

    $smarty->assign("SEARCH_RESULT_COUNT", count($results));

    $smarty->assign("SEARCH_RESULTS", $data);
    
    if ($_GET['ajax'] == 1)
    $core->template = "search/results.tpl";
    else
    $body_template = "search/results.tpl";

 