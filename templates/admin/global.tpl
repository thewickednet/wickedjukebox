						<h1><a name="intro" id="intro"></a>Admin</h1>

						{include file='admin/top_menu.tpl'}

            <h3>Global Settings</h3>
            <form method="post">
            <table cellpadding="2" cellspacing="4">
            {foreach from=$GLOBAL_SETTINGS item=GLOBAL_SETTING}            
                <tr>
                    <td valign="top"><input type="text" value="{$GLOBAL_SETTING.value}" name="{$GLOBAL_SETTING.var}" maxlength="255" size="32" /></td>
                    <td valign="top">{$GLOBAL_SETTING.comment}</td>
                </tr>
            {/foreach}
            </table>
			
            <h3>Channel Settings</h3>
            
            <table cellpadding="2" cellspacing="4">
            {foreach from=$CHANNEL_SETTINGS item=CHANNEL_SETTING}            
                <tr>
                    <td valign="top"><input type="text" value="{$CHANNEL_SETTING.value}" name="{$CHANNEL_SETTING.var}" maxlength="255" size="32" /></td>
                    <td valign="top">{$CHANNEL_SETTING.comment}</td>
                </tr>
            {/foreach}
            </table>
			
			<p><input type="submit" value="save" name="submit"></p>
			</form>