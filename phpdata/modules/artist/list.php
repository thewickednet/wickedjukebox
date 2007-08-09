<?php


if (empty($_GET['param'])) 
    $alpha = "a";
else {
    $alpha = $_GET['param'];
    $core->template = 'artist/list.tpl';
}

$cache_key = sprintf("list_artist_%s", $alpha);

if(!$artists = $cache->load($cache_key)) {
    
    $artists = Artist::getByAlpha($alpha);
    $cache->save($artists, $cache_key);
}

if (!empty($_GET['pagenum']))
    $core->template = 'artist/list_results.tpl';


    require_once 'Pager/Pager.php';
    $params = array(
        'mode'      => 'Sliding',
        'perPage'   => 20,
        'delta'     => 5,
        'append'    => false,
        'urlVar'    => 'pagenum',
        'path'      => '',
        'fileName'  => 'javascript:blaatOver(%d)',
        'itemData'  => $artists
    );

    $pager = & Pager::factory($params);
    $data  = $pager->getPageData();
    $links = $pager->getLinks();

    $smarty->assign("LINKS", $links['all']);



$smarty->assign("ALPHA_INDEX", Core::buildAlphaList());
$smarty->assign("ALPHA", $alpha);
$smarty->assign("ARTISTS", $data);
$body_template = "artist/list.tpl";

?>