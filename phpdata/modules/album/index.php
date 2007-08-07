<?php


switch ($_GET['action']) {
    case "detail":
        include "../phpdata/modules/album/detail.php";
    break;
    default:
    case "list":
        include "../phpdata/modules/album/list.php";
    break;
}

?>