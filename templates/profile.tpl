          <h1>My Jukebox</h1>
          <p>logged in as <b>{$CORE->userdata.fullname}</b> - <a href="#" onclick="javascript:logout();">logout</a></p>
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
          <b>Group:</b> {$CORE->permissions.title}<br />
          <b>Credits:</b> {$CORE->userdata.credits}<br />
          </p>
