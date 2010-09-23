<?php

$player_status = BackendDB::getCurrentSong($core->channel_id);

$smarty->assign("PLAYER_STATUS", $player_status);

$core->template = "get_current.tpl";

