
            <h1><a name="intro" id="intro"></a>Artist Details</h1>

            <h2>{$ARTIST.name}</h2>


            {if $ARTIST.name eq 'Various Artists' || $ARTIST.name eq 'Soundtracks' || $ARTIST.name eq 'Video Games'}
            <h3>Songs in this category</h3>
            {else}
                <img src="/img.php?category=artist&preset=detail&id={$ARTIST.id}" style="border: 1px solid #cccccc; background-color: #ffffff; padding: 3px; margin-right: 2px; margin-top: 3px;" id="img_artist"/>
            <h3>Songs by this artist</h3>
	    {/if}
            <div id="results">
            <table>
            {foreach from=$SONGS item=SONG}
              <tr>
                <td width="24">{if $CORE->permissions.queue_add eq '1'}<a href="#" onclick="javascript:addsong({$SONG.song_id});"><img src="/images/bullet_add.png" class="button" /></a>{/if}</td>
                <td><a href="/details/song/{$SONG.song_id}/">{$SONG.title}</a></td>
                <td width="24">{if $CORE->permissions.queue_add eq '1'}<a href="#" onclick="javascript:addalbum({$SONG.album_id});"><img src="/images/bullet_add.png" class="button" /></a>{/if}</td>
                <td><a href="/details/album/{$SONG.album_id}/">{$SONG.album_name}</a></td>
                <td align="right">{$SONG.duration|date_format:"%M:%S"}</td>
              </tr>
            {/foreach}
            <tr>
            <td colspan="5" align="center">{$LINKS}</td>
            </tr>
            </table>
            </div>
            