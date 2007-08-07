						<h1><a name="intro" id="intro"></a>Album Details</h1>

            <h2>{$ALBUM.name}{if $CORE->permissions.queue_add eq '1'} <a href="#" onclick="javascript:addalbum({$ALBUM.id});"><img src="/images/bullet_add.png" class="button" /></a>{/if}</h2>

            <table cellspacing="6" width="750">
            <tr>
              <td>Artist:</b> <a href="/details/artist/{$ARTIST.id}/">{$ARTIST.name}</a></td>
              <td rowspan="4" align="right">
              {if $COVER ne ''}
              <img src="/browse/albums/cover/{$ALBUM.album_id}/" border="0" id="img_album"/>
              {/if}
              </td>
            </tr>
            <tr>
              <td><b>Added to DB:</b> {$ALBUM.added|date_format:"%d.%m.%Y@%H:%M:%S"}</td>
            </tr>
            <tr>
              <td><b>Downloaded:</b> {$ALBUM.downloaded}</td>
            </tr>
            <tr>
              <td><a href="/download/album/{$ALBUM.album_id}/">Download Album</a></td>
            </tr>
            </table>

            <h3>Songs on this album</h3>
            <div id="results">
            <table cellspacing="6">
            {foreach from=$SONGS item=SONG}
              <tr>
                <td width="24">{if $CORE->permissions.queue_add eq '1'}<a href="#" onclick="javascript:addsong({$SONG.id});"><img src="/images/bullet_add.png" class="button" /></a>{/if}</td>
                <td>{$SONG.track_no} - <a href="/details/song/{$SONG.id}/">{$SONG.title}</a></td>
                <td align="right">{$SONG.duration|date_format:"%M:%S"}</td>
              </tr>
            {/foreach}
            </table>
            </div>
