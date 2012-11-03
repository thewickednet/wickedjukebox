<?php

    $results = Search::onlyArtist($search_pattern);

    $smarty->assign("PREVIEW_RESULTS", $results);
    
    $core->template = 'search/preview.tpl';

                
