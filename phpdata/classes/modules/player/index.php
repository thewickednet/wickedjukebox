<?

if ($_GET['action'] == "update")
    $core->template = 'player/info.tpl';
else 
    $core->template = 'player/base.tpl';
