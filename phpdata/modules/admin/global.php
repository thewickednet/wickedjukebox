<?


    $global_settings = Settings::getGlobalSettings();
    $channel_settings = Settings::getChannelSettings($core->channel_id);

    if ($_POST['submit'] == 'save') {
        
        
        foreach ($global_settings as $global_setting) {
            $key = $global_setting['var'];
            $value = stripslashes(trim($_POST[$key]));
            Settings::setGlobalSettings($key, $value);
        }
        
        foreach ($channel_settings as $channel_setting) {
            $key = $channel_setting['var'];
            $value = stripslashes(trim($_POST[$key]));
            Settings::setChannelSettings($core->channel_id, $key, $value);
        }
        
    }
    
    $global_settings = Settings::getGlobalSettings();
    $channel_settings = Settings::getChannelSettings($core->channel_id);

    $smarty->assign("GLOBAL_SETTINGS", $global_settings);
    $smarty->assign("CHANNEL_SETTINGS", $channel_settings);

    $body_template = "admin/global.tpl";

?>