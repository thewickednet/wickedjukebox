<?php
	
	$setting = Settings::getChannelSetting($core->channel_id, $core->user_id, $_GET['action']);
	
	
	if ($setting['value'] == 1)
	  $setting = 0;
	else 
	  $setting = 1;
	  
  Settings::setChannelSettings($core->channel_id, $core->user_id, $_GET['action'], $setting);

  include "../phpdata/modules/auth/refresh.php";

?>