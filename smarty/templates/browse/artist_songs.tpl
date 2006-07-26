
						<h1><a name="intro" id="intro"></a>Browse by artists</h1>

						<p>
            {foreach from=$ALPHA_INDEX item=ALPHA}
            <a href="/browse/artists/byalpha/{$ALPHA.alpha|lower}/">{$ALPHA.alpha}</a>
            {/foreach}
            </p>
            <h2>{$ARTIST.name}</h2>

            {if $COVER ne ''}
            <img src="/browse/artists/cover/{$ARTIST.artist_id}/" border="0" />
            {/if}

            <h3>Songs by this artist</h3>
            <div id="results">
            <table>
            {foreach from=$SONGS item=SONG}
              <tr>
                <td width="24"><a href="#" onclick="javascript:addsong({$SONG.song_id});"><img src="/images/add.gif" border="0" /></a></td>
                <td><a href="/details/song/{$SONG.song_id}/">{$SONG.song}</a></td>
                <td width="24"><a href="#" onclick="javascript:addalbum({$SONG.album_id});"><img src="/images/add.gif" border="0" /></a></td>
                <td><a href="/browse/albums/byid/{$SONG.album_id}/">{$SONG.album}</a></td>
                <td align="right">{$SONG.duration|date_format:"%M:%S"}</td>
              </tr>
            {/foreach}
            </table>
            </div>