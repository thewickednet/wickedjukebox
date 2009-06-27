<h1>My Jukebox</h1>

          <p>
          <img src="/images/user_gray.png" title="user" />&nbsp;&nbsp;&nbsp;&nbsp;<b>{$CORE->userdata.fullname}</b> ({$CORE->permissions.title})&nbsp;&nbsp;&nbsp;
          <img src="/images/money.png" title="credits" />&nbsp;&nbsp;<b>{$CORE->userdata.credits}</b><br />
          <img src="/images/music.png" title="tune in!" />&nbsp;&nbsp;&nbsp;&nbsp;<b>Tune In! <a href="http://jukebox.wicked.lu/wicked.pls">External</a> or <a href="javascript:;" onclick="javascript:openPlayer();">Flash</a> Player!</b><br />
          <a href="javascript:;" onclick="javascript:setStandingAffects('loves_affect_random', 'splash');"><img src="/images/thumb_up.png" title="my loves affect random, click to toggle" border="0" class="icon{if $PLAYER_STATUS.loves_affect_random == '1'}a{/if}"/></a><a href="javascript:;" onclick="javascript:setStandingAffects('hates_affect_random', 'splash');"><img src="/images/thumb_down.png" title="my hates affect random, click to toggle" border="0" class="icon{if $PLAYER_STATUS.hates_affect_random == '1'}a{/if}"/></a>
          </p>
<!--
            <p>Radio users: {$ICECAST.1->listeners} / Website users: {$ALIVE_USERS_COUNT}</p>
-->
            {if count($ALIVE_USERS) > 0}
            <p>
            {foreach name="ulist" from=$ALIVE_USERS item=ALIVE_USER}
            <a href="/user/detail/{$ALIVE_USER.id}/"><img src="/img.php?category=user&preset=icon&id={$ALIVE_USER.id}" style="border: 1px solid #cccccc; background-color: #ffffff; padding: 3px; margin-right: 2px; margin-top: 3px; {if $ALIVE_USER.listen > 180}filter:alpha(opacity=05);-moz-opacity:.50;opacity:.50;{/if}" id="img_album" title="{$ALIVE_USER.fullname}"/></a>&nbsp;
            {/foreach}
            </p>
            {else}
            <p>no user online</p>
            {/if}
