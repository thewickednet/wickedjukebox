<?php

$core->active_node = "album";

switch ($_GET['action']) {
    case "latest":
        include "../phpdata/modules/album/latest.php";
    break;
	case "detail":
        include "../phpdata/modules/album/detail.php";
    break;
    case "download":
        include "../phpdata/modules/album/download.php";
    break;
    default:
    case "list":
        include "../phpdata/modules/album/list.php";
    break;
}

?>