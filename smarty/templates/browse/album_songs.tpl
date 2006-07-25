						<h1><a name="intro" id="intro"></a>Browse by albums</h1>

						<p>
            {foreach from=$ALPHA_INDEX item=ALPHA}
            <a href="/browse/artists/byalpha/{$ALPHA.alpha|lower}/">{$ALPHA.alpha}</a>
            {/foreach}
            </p>

            <h3>Songs on Album: {$ALBUM.title}</h3>

            <div id="results">
            <table>
            {foreach from=$SONGS item=SONG}
              <tr>
                <td>+ i {$SONG.song}</td>
                <td>{$ARTIST.0.name}</td>
                <td align="right">{$SONG.duration|date_format:"%M:%S"}</td>
              </tr>
            {/foreach}
            </table>
            </div>