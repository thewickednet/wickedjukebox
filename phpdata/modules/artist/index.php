<?php


switch ($_GET['action']) {
    case "detail":
        include "../phpdata/modules/artist/detail.php";
    break;
    default:
    case "list":
        include "../phpdata/modules/artist/list.php";
    break;
}

?>