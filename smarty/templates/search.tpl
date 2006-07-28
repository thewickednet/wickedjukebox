
						<h1><a name="intro" id="intro"></a>Search</h1>

            <h2>You were looking for "{$SEARCH_PATTERN}" in "{$SEARCH_MODE}"</h2>

            <h3>Results</h3>
            <div id="results">
            {if count($RESULTS) ne '0'}
            <table>
            {foreach from=$RESULTS item=RESULT}
              <tr>
                <td><a href="/browse/artists/byid/{$RESULT.artist_id}/">{$RESULT.artist}</a></td>
                <td width="24"><a href="#" onclick="javascript:addsong({$RESULT.song_id});"><img src="/images/add.gif" border="0" /></a></td>
                <td><a href="/details/song/{$RESULT.song_id}/">{$RESULT.song}</a></td>
                <td width="24"><a href="#" onclick="javascript:addalbum({$RESULT.album_id});"><img src="/images/add.gif" border="0" /></a></td>
                <td><a href="/browse/albums/byid/{$RESULT.album_id}/">{$RESULT.album}</a></td>
                <td align="right">{$RESULT.duration|date_format:"%M:%S"}</td>
              </tr>
            {/foreach}
            </table>
            {else}
            <p>no results found</p>
            {/if}
            </div>
