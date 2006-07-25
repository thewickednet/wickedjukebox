						<h1><a name="intro" id="intro"></a>Browse by artists</h1>

						<p>
            {foreach from=$ALPHA_INDEX item=ALPHA}
            <a href="/browse/artists/byalpha/{$ALPHA.alpha|lower}/">{$ALPHA.alpha}</a>
            {/foreach}
            </p>
            <h3>Songs for Artist: {$ARTIST.name}</h3>

            <div id="results">
            <table>
            {foreach from=$SONGS item=SONG}
              <tr>
                <td>{$SONG.song}</td>
                <td>{$SONG.album}</td>
                <td align="right">{$SONG.duration|date_format:"%M:%S"}</td>
              </tr>
            {/foreach}
            </table>
            </div>