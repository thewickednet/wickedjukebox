<?php


if ($core->permissions['admin'] != 1) {
    header("Location: /");
    exit();
}


$core->active_node = "admin";


switch ($_GET['action']) {
    case "users":
        include "../phpdata/modules/admin/users.php";
    break;
    default:
    case "global":
        include "../phpdata/modules/admin/global.php";
    break;
}

?>