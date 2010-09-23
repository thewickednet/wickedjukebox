						<h1><a name="intro" id="intro"></a>User Profile</h1>

            <h2>{$USER.fullname}</h2>

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

