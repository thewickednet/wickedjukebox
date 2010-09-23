<?

    $core->active_node = "latest";

    $latest = Song::getLatest();

    $smarty->assign("RESULTS", $latest);
    
    $body_template = "song/latest.tpl";




?>