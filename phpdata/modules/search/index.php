<?php

$core->active_node = "search";

$search_pattern = $_POST['pattern'];
$search_mode = $_POST['mode'];

$smarty->assign("SEARCH_PATTERN", $search_pattern);
$smarty->assign("SEARCH_MODE", $search_mode);

switch ($_GET['action']) {
    case "preview":
        include "../phpdata/modules/search/preview.php";
    break;
    case "engine":
    default:
        include "../phpdata/modules/search/engine.php";
    break;
}
 
