						<h1><a name="intro" id="intro"></a>Album Details</h1>

            <h2>{if $CORE->permissions.queue_add eq '1'} <a href="javascript:;" onclick="javascript:addalbum({$ALBUM.id});"><img src="/images/add.png" title="queue the entire album" class="button" /></a>{/if} {$ALBUM.name} ({$ALBUM.cost} <img src="/images/money.png" class="button" />)</h2>

            <table cellspacing="6" width="700">
            <tr>
              <td>
              {if $ALBUM.type eq 'ost'}
              <a href="javascript:;" onclick="javascript:listSpecial('ost');">Original Motion Picture Soundtrack</a>
              {/if}
              {if $ALBUM.type eq 'various'}
              <a href="javascript:;" onclick="javascript:listSpecial('various');">Various Artists</a>
              {/if}
              {if $ALBUM.type eq 'game'}
              <a href="javascript:;" onclick="javascript:listSpecial('game');">Game Soundtrack</a>
              {/if}
              </td>
              <td rowspan="4" align="right">
                <img src="/img.php?category=album&preset=detail&id={$ALBUM.id}" style="border: 1px solid #cccccc; background-color: #ffffff; padding: 3px; margin-right: 2px; margin-top: 3px;" id="img_album"/>
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
                <td width="24">{if $CORE->permissions.queue_add eq '1'}<a href="javascript:;" onclick="javascript:addsong({$SONG.id});"><img src="/images/bullet_add.png" class="button" /></a>{/if}</td>
                <td>{$SONG.track_no|string_format:"%02d"} - <a href="/details/song/{$SONG.artist_id}/">{$SONG.artist_name}</a></td>
                <td><a href="/details/song/{$SONG.id}/">{$SONG.title}</a></td>
                <td align="right">{$SONG.duration|date_format:"%M:%S"} ({$SONG.cost} <img src="/images/money.png" class="button" />)</td>
              </tr>
            {/foreach}
            </table>
            </div>
