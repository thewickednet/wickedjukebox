<?php


$search_pattern = $_GET['pattern'];


$smarty->assign("SEARCH_PATTERN", $search_pattern);
$smarty->assign("SEARCH_MODE", $_GET['action']);


$original = array("&","'",":","/","@","é", "à", "ü", "è", "ä", "ö", " ");
$entities = array("AND","QUOTE","DOUBLES","SLASH","AT","EE", "AE", "UE", "EE", "AA", "OE", "_");


$cache_key = str_replace($original, $entities, utf8_decode($search_pattern));


if (strlen($search_pattern) < 3) {

    $smarty->assign("ERROR_MESSAGE", "Search pattern must be at least 3 characters long!");

} elseif (strlen($search_pattern) > 20) {

    $smarty->assign("ERROR_MESSAGE", "Search pattern shouldn't be longer than 20 characters!");

} else {

    if(!$results = $cache->load($cache_key)) {
    
        switch ($_GET['action']) {
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
                $results = Search::byAny($search_pattern);
            break;
        }
    
        for ($i = 0; $i < count($results); $i++) {
            $results[$i]['cost'] = Song::evaluateCost($results[$i]['duration']);
        }
    
        //$artists = Artist::getByAlpha($alpha);
        $cache->save($results, $cache_key);
    }

}


    require_once 'Pager/Pager.php';
    $params = array(
        'mode'      => 'Sliding',
        'perPage'   => 20,
        'delta'     => 8,
        'append'    => false,
        'urlVar'    => 'pagenum',
        'path'      => '',
        'prevImg'   => '<img src="/images/resultset_previous.png" border="0" />',
        'nextImg'   => '<img src="/images/resultset_next.png" border="0" />',
        'fileName'  => sprintf("javascript:blaatOverSearch(%%d, '%s')", $_GET['target']),
        'itemData'  => $results
    );

    $pager = & Pager::factory($params);
    $data  = $pager->getPageData();
    $links = $pager->getLinks();

    $smarty->assign("LINKS", $links['all']);

    $smarty->assign("RESULT_COUNT", count($results));

    
    $smarty->assign("RESULTS", $data);
    
    $core->template = "search.tpl";

?>