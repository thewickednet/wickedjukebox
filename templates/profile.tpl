          <h1>My Jukebox</h1>
          <p><img src="/images/user_gray.png" title="user" />&nbsp;&nbsp;&nbsp;&nbsp;<b>{$CORE->userdata.fullname}</b> ({$CORE->permissions.title})&nbsp;&nbsp;&nbsp;
          <img src="/images/money.png" title="credits" />&nbsp;&nbsp;&nbsp;&nbsp;<b>{$CORE->userdata.credits}</b><br />
          <img src="/images/music.png" title="tune in!" />&nbsp;&nbsp;&nbsp;&nbsp;<b>Tune In! <a href="http://wickedjukebox.com/wicked.pls">External</a> or <a href="javascript:;" onclick="javascript:openPlayer();">Flash</a> Player!</b><br />
                    <a href="javascript:;" onclick="javascript:setStandingAffects('loves_affect_random', 'login');"><img src="/images/thumb_up.png" title="my loves affect random, click to toggle" border="0" class="icon{if $PLAYER_STATUS.loves_affect_random == '1'}a{/if}"/></a><a href="javascript:;" onclick="javascript:setStandingAffects('hates_affect_random', 'login');"><img src="/images/thumb_down.png" title="my hates affect random, click to toggle" border="0" class="icon{if $PLAYER_STATUS.hates_affect_random == '1'}a{/if}"/></a>
          </p>

          {if count($CHANNEL_LIST) > 1}
          <p><form>
          Channel:
          <select name="channel_changer" id="channel_changer" onchange="javascript:changeChannel()">
          {html_options options=$CHANNEL_LIST selected=$CORE->channel_id}
          </select>
        </form>
          </p>
          {/if}
          <p>
          </p>
