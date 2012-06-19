<?php


if (empty($_GET['param'])) 
    $alpha = "a";
else 
    $alpha = $_GET['param'];

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
        'prevImg'   => '<img src="/images/resultset_previous.png" border="0" />',
        'nextImg'   => '<img src="/images/resultset_next.png" border="0" />',
        'fileName'  => 'javascript:blaatOver(%d)',
        'itemData'  => $artists
    );

    $pager = & Pager::factory($params);
    $data  = $pager->getPageData();
    $links = $pager->getLinks();

    $smarty->assign("LINKS", $links['all']);

    $smarty->assign("ALPHA_INDEX", Core::buildAlphaList());
    $smarty->assign("ALPHA", $alpha);
    $smarty->assign("RESULT_COUNT", count($artists));
    $smarty->assign("ARTISTS", $data);

    $body_template = "artist/list.tpl";
