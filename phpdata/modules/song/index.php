<?php

$core->active_node = "artist";


switch ($_GET['action']) {
    case "detail":
        include "../phpdata/modules/song/detail.php";
    break;
    case "randomize":
        include "../phpdata/modules/song/random.php";
    break;
    default:
        header("Location: /");
    break;
}

?>