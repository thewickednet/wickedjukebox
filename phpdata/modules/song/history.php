<?php 

    $core->active_node = "history";

    $history = Song::getHistory();

    $smarty->assign("RESULTS", $history);
    
    $body_template = "song/history.tpl";

?>