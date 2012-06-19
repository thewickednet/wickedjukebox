<?php

$core->active_node = "splash";

switch ($_GET['action']) {
    case "search":
        include "../phpdata/modules/splash/search.php";
    break;
    case "report":
        include "../phpdata/modules/splash/report.php";
    break;
}
