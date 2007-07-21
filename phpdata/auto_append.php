<?php

$smarty->assign("USERINFO", $core->userinfo);
$smarty->assign("PERMISSIONS", $core->permissions);


if ($core->display)
    $smarty->display($core->template);







?>
