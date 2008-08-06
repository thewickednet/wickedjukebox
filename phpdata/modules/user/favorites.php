<?
    if (empty($_GET['param']) && empty($_POST['param']))
        $user_id = $core->user_id;
    elseif (!empty($_GET['param']))
        $user_id = $_GET['param'];
    elseif (!empty($_POST['param']))
        $user_id = $_POST['param'];

    $user = User::getUser($user_id);

    $core->active_node = "favorites";

    $cache_key = sprintf("favorites_%d", $user_id);
    
    if(!$results = $cache->load($cache_key)) {
        
        $results = User::getFavorites($user_id, "love");
        $cache->save($results, $cache_key);
    }

    if (!empty($_GET['pagenum']))
        $core->template = 'user/favorites_results.tpl';

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
        'fileName'  => 'javascript:blaatOverUser(%d)',
        'itemData'  => $results
    );

    $pager = & Pager::factory($params);
    $data  = $pager->getPageData();
    $links = $pager->getLinks();

    $smarty->assign("LINKS", $links['all']);

    $smarty->assign("RESULT_COUNT", count($results));

    $smarty->assign("USERS", User::getAll());
    $smarty->assign("USER", $user);
    $smarty->assign("RESULTS", $data);
    
    $body_template = "user/favorites.tpl";


?>