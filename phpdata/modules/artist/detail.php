<?php



$artist = Artist::getById($_GET['param']);


$cache_key = sprintf("detail_artist_%s", $_GET['param']);

if(!$songs = $cache->load($cache_key)) {
    
    $songs = Artist::getSongs($_GET['param']);
    
    for ($i = 0; $i < count($songs); $i++) {
        $songs[$i]['cost'] = Song::evaluateCost($songs[$i]['duration']);
    }
    
    $cache->save($songs, $cache_key);
}



if (!empty($_GET['pagenum']))
    $core->template = 'artist/detail_results.tpl';

    require_once 'Pager/Pager.php';
    $params = array(
        'mode'      => 'Sliding',
        'perPage'   => 20,
        'delta'     => 5,
        'append'    => false,
        'urlVar'    => 'pagenum',
        'path'      => '',
        'prevImg'   => '<img src="/images/resultset_previous.png" border="0" />',
        'nextImg'   => '<img src="/images/resultset_next.png" border="0" />',
        'fileName'  => 'javascript:blaatOverDetail(%d)',
        'itemData'  => $songs
    );

    $pager = & Pager::factory($params);
    $data  = $pager->getPageData();
    $links = $pager->getLinks();

    $smarty->assign("LINKS", $links['all']);


$smarty->assign("RESULT_COUNT", count($songs));
$smarty->assign("SONGS", $data);
$smarty->assign("ARTIST", $artist);
$body_template = "artist/detail.tpl";

?>