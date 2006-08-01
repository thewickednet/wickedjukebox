						<h1><a name="intro" id="intro"></a>Statistics</h1>
            <div id="results">

            <h3>Total</h3>
            <table cellspacing="6">
              <tr>
                <td width="15">&nbsp;</td>
                <td>Users</td>
                <td align="right">{$USER_TOTAL.0}</td>
              </tr>
              <tr>
                <td width="15">&nbsp;</td>
                <td>Artists</td>
                <td align="right">{$ARTIST_TOTAL.0}</td>
              </tr>
              <tr>
                <td width="15">&nbsp;</td>
                <td>Albums</td>
                <td align="right">{$ALBUM_TOTAL.0}</td>
              </tr>
              <tr>
                <td width="15">&nbsp;</td>
                <td>Songs</td>
                <td align="right">{$SONG_TOTAL.0}</td>
              </tr>
            </table>


            <h3>Albums - Queued</h3>
            <table cellspacing="6">
            {counter start=0 print=false}
            {foreach from=$ALBUM_PLAYS item=ALBUM_PLAY}
              <tr>
                <td width="15">{counter}.</td>
                <td><a href="/browse/albums/byid/{$ALBUM_PLAY.album_id}/">{$ALBUM_PLAY.title}</a></td>
                <td align="right">{$ALBUM_PLAY.played}</td>
              </tr>
            {/foreach}
            </table>


            <h3>Albums - Downloaded</h3>
            <table cellspacing="6">
            {counter start=0 print=false}
            {foreach from=$ALBUM_DOWNLOADS item=ALBUM_DOWNLOAD}
              <tr>
                <td width="15">{counter}.</td>
                <td><a href="/browse/albums/byid/{$ALBUM_DOWNLOAD.album_id}/">{$ALBUM_DOWNLOAD.title}</a></td>
                <td align="right">{$ALBUM_DOWNLOAD.downloaded}</td>
              </tr>
            {/foreach}
            </table>


            <h3>Songs - Queued</h3>
            <table cellspacing="6">
            {counter start=0 print=false}
            {foreach from=$SONG_PLAYS item=SONG_PLAY}
              <tr>
                <td width="15">{counter}.</td>
                <td><a href="/details/song/{$SONG_PLAY.song_id}/">{$SONG_PLAY.title}</a></td>
                <td align="right">{$SONG_PLAY.played}</td>
              </tr>
            {/foreach}
            </table>


            <h3>Songs - Downloaded</h3>
            <table cellspacing="6">
            {counter start=0 print=false}
            {foreach from=$SONG_DOWNLOADS item=SONG_DOWNLOAD}
              <tr>
                <td width="15">{counter}.</td>
                <td><a href="/details/song/{$SONG_DOWNLOAD.song_id}/">{$SONG_DOWNLOAD.title}</a></td>
                <td align="right">{$SONG_DOWNLOAD.downloaded}</td>
              </tr>
            {/foreach}
            </table>


            <h3>Users - Queued Songs</h3>
            <table cellspacing="6">
            {counter start=0 print=false}
            {foreach from=$USER_PLAYS item=USER_PLAY}
              <tr>
                <td width="15">{counter}.</td>
                <td>{$USER_PLAY.fullname}</td>
                <td align="right">{$USER_PLAY.selects}</td>
              </tr>
            {/foreach}
            </table>

            <h3>Users - Downloaded Songs</h3>
            <table cellspacing="6">
            {counter start=0 print=false}
            {foreach from=$USER_DOWNLOADS item=USER_DOWNLOAD}
              <tr>
                <td width="15">{counter}.</td>
                <td>{$USER_DOWNLOAD.fullname}</td>
                <td align="right">{$USER_DOWNLOAD.downloads}</td>
              </tr>
            {/foreach}
            </table>

            <h3>Users - Skipped Songs</h3>
            <table cellspacing="6">
            {counter start=0 print=false}
            {foreach from=$USER_SKIPS item=USER_SKIP}
              <tr>
                <td width="15">{counter}.</td>
                <td>{$USER_SKIP.fullname}</td>
                <td align="right">{$USER_SKIP.skips}</td>
              </tr>
            {/foreach}
            </table>

            </div>