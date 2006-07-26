						<h1><a name="intro" id="intro"></a>Browse by albums</h1>

						<p>
            {foreach from=$ALPHA_INDEX item=ALPHA}
            <a href="/browse/albums/byalpha/{$ALPHA.alpha|lower}/">{$ALPHA.alpha}</a>
            {/foreach}
            </p>

            <h2>{$ALBUM.title}&nbsp;&nbsp;<a href="#" onclick="javascript:addalbum({$ALBUM.album_id});"><img src="/images/add.gif" border="0" /></a></h2>

            <table cellspacing="6" width="750">
            <tr>
              <td>Artist: <a href="/browse/artist/byid/{$ARTIST.0.artist_id}/">{$ARTIST.0.name}</a></td>
              <td rowspan="3" align="right">
              {if $COVER ne ''}
              <img src="/browse/albums/cover/{$ALBUM.album_id}/" border="0" />
              {/if}
              </td>
            </tr>
            <tr>
              <td>Added to DB: {$ALBUM.added|date_format:"%d.%m.%Y@%H:%M:%S"}</td>
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
                <td width="24"><a href="#" onclick="javascript:addsong({$SONG.song_id});"><img src="/images/add.gif" border="0" /></a></td>
                <td>{$SONG.track_no} - <a href="/details/song/{$SONG.song_id}/">{$SONG.song}</a></td>
                <td align="right">{$SONG.duration|date_format:"%M:%S"}</td>
              </tr>
            {/foreach}
            </table>
            </div>
