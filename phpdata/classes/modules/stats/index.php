<?php

$core->active_node = "stats";


switch ($_GET['action']) {
    case "users":
        include "../phpdata/modules/stats/users.php";
    break;
    default:
    case "jukebox":
        include "../phpdata/modules/stats/jukebox.php";
    break;
}

?>