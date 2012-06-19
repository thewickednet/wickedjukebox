<?

    $core->active_node = "latest";

    $latest = Album::getLatest(100);

    $smarty->assign("RESULTS", $latest);
    
    $body_template = "album/latest.tpl";


