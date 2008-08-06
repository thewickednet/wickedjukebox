<?php

$core->active_node = "user";


switch ($_GET['action']) {
    case "latest":
        include "../phpdata/modules/user/latest.php";
    break;
    case "favorites":
        include "../phpdata/modules/user/favorites.php";
    break;
    case "profile":
        include "../phpdata/modules/user/profile.php";
    break;
    case "detail":
        include "../phpdata/modules/user/detail.php";
    break;
    case "report":
        include "../phpdata/modules/user/report.php";
    break;
    case "randomize":
        include "../phpdata/modules/user/random.php";
    break;
    default:
        header("Location: /");
    break;
}

?>