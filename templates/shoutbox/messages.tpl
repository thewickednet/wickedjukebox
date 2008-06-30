            <ul id="shout_list">
			{foreach from=$SHOUTBOX item=SHOUTER}
			<li style="color: rgb({$SHOUTER.color|floor},{$SHOUTER.color|floor},{$SHOUTER.color|floor});">{$SHOUTER.message|utf8_encode} [{$SHOUTER.fullname}]</li>
			{/foreach}
            </ul>            
            
