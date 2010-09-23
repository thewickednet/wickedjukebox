<?php

$core->active_node = "artist";


switch ($_GET['action']) {
    case "latest":
        include "../phpdata/modules/song/latest.php";
    break;
    case "history":
        include "../phpdata/modules/song/history.php";
    break;
    case "detail":
        include "../phpdata/modules/song/detail.php";
    break;
    case "download":
        include "../phpdata/modules/song/download.php";
    break;
    case "report":
        include "../phpdata/modules/song/report.php";
    break;
    case "randomize":
        include "../phpdata/modules/song/random.php";
    break;
    default:
        header("Location: /");
    break;
}

?>