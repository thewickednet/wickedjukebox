<?php

$core->active_node = "artist";


switch ($_GET['action']) {
    case "detail":
        include "../phpdata/modules/song/detail.php";
    break;
    default:
        header("Location: /");
    break;
}

?>