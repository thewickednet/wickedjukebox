<?php

$core->active_node = "event";

switch ($_GET['action']) {
	case "detail":
        include "../phpdata/modules/event/detail.php";
    break;
	default:
    case "list":
        include "../phpdata/modules/event/list.php";
    break;
}

