            <ul id="shout_list">
			{foreach from=$SHOUTBOX item=SHOUTER}
			<li {if $SHOUTER.age > 0}class="old"{/if}>{$SHOUTER.message|utf8_encode} [{$SHOUTER.fullname}]</li>
			{/foreach}
            </ul>            
            