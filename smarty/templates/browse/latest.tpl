
						<h1><a name="intro" id="intro"></a>Browse latest</h1>

            <div id="results">
            <table>
            {foreach from=$SONGS item=SONG}
              <tr>
                <td><a href="/browse/artists/byid/{$SONG.artist_id}/">{$SONG.name}</a></td>
                <td width="24">{if $PERMISSIONS.queue_add eq '1'}<a href="#" onclick="javascript:addsong({$SONG.song_id});"><img src="/images/add.gif" border="0" /></a>{/if}</td>
                <td><a href="/details/song/{$SONG.song_id}/">{$SONG.song}</a></td>
                <td width="24">{if $PERMISSIONS.queue_add eq '1'}<a href="#" onclick="javascript:addalbum({$SONG.album_id});"><img src="/images/add.gif" border="0" /></a>{/if}</td>
                <td><a href="/browse/albums/byid/{$SONG.album_id}/">{$SONG.album}</a></td>
                <td align="right">{$SONG.duration|date_format:"%M:%S"}</td>
              </tr>
            {/foreach}
            <tr>
            <td colspan="6" align="center">{$LINKS}</td>
            </tr>
            </table>
            </div>
            {debug}
