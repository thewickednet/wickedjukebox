<h1>My Jukebox</h1>

          <p><img src="/images/user_gray.png" title="user" />&nbsp;&nbsp;&nbsp;&nbsp;<b>{$CORE->userdata.fullname}</b> ({$CORE->permissions.title}) <a href="/index.php?module=auth&mode=logout"><img src="/images/logout.png" border="0" title="logout" /></a><br />
          <img src="/images/money.png" title="credits" />&nbsp;&nbsp;&nbsp;&nbsp;<b>{$CORE->userdata.credits}</b><br />
          <img src="/images/music.png" title="tune in!" />&nbsp;&nbsp;&nbsp;&nbsp;<b>Tune In! <a href="http://jukebox.wicked.lu/wicked.pls">External</a> or <a href="javascript:;" onclick="javascript:openPlayer();">Flash</a> Player!</b><br />
          
          </p>

            <p>Radio users: {$ICECAST.0->listeners} / Website users: {$ALIVE_USERS_COUNT}</p>
            {if count($ALIVE_USERS) > 0}
            <p>
            {foreach name="ulist" from=$ALIVE_USERS item=ALIVE_USER}
            <a href="/user/detail/{$ALIVE_USER.id}/"><img src="/img.php?category=user&preset=icon&id={$ALIVE_USER.id}" style="border: 1px solid #cccccc; background-color: #ffffff; padding: 3px; margin-right: 2px; margin-top: 3px;" id="img_album" title="{$ALIVE_USER.fullname}"/></a>&nbsp;
            {/foreach}
            </p>
            {else}
            <p>no user online</p>
            {/if}
