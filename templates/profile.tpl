          <h1>My Jukebox</h1>
          <p><img src="/images/user_gray.png" />&nbsp;&nbsp;<b>{$CORE->userdata.fullname}</b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="javascript:;" onclick="javascript:logout();"><img src="/images/logout.png" border="0" /></a></p>
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
          <img src="/images/group.png" />&nbsp;&nbsp;<b>{$CORE->permissions.title}</b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<img src="/images/money.png" /></b> <b>{$CORE->userdata.credits}</b>
          </p>
