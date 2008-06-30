          <h1>My Jukebox</h1>
          <p><img src="/images/user_gray.png" title="user" />&nbsp;&nbsp;&nbsp;&nbsp;<b>{$CORE->userdata.fullname}</b> ({$CORE->permissions.title})<br />
          <img src="/images/money.png" title="credits" />&nbsp;&nbsp;&nbsp;&nbsp;<b>{$CORE->userdata.credits}</b><br />
          <img src="/images/music.png" title="tune in!" />&nbsp;&nbsp;&nbsp;&nbsp;<b>Tune In! <a href="http://jukebox.wicked.lu/wicked.pls">External</a> or <a href="javascript:;" onclick="javascript:openPlayer();">Flash</a> Player!</b><br />
          
          <a href="/index.php?module=auth&mode=logout"><img src="/images/logout.png" border="0" title="logout" /></a>&nbsp;&nbsp;&nbsp;&nbsp;<a href="/index.php?module=auth&mode=logout">Logout</a></p>
          
          {if count($CHANNEL_LIST) > 1}
          <p><form>
          Channel:
          <select name="channel_changer" id="channel_changer">
          {html_options options=$CHANNEL_LIST selected=$CORE->channel_id}
          </select>
        </form>
          </p>
          {/if}
          <p>
          </p>
