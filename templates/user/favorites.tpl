
            <h1><a name="intro" id="intro"></a>My Favorites</h1>

            <div id="results">
                {if count($RESULTS) ne '0'}
                <p align="center">{$LINKS}</p>
                <table cellspacing="1" cellpadding="4">
                {foreach from=$RESULTS item=RESULT}
                  <tr class="resultlist">
                    <td><a href="/details/artists/{$RESULT.artist_id}/">{$RESULT.artist_name}</a></td>
                    <td><a href="#" onclick="javascript:addsong({$RESULT.song_id});"><img src="/images/bullet_add.png" class="button" /></a> <a href="/details/song/{$RESULT.song_id}/">{$RESULT.song_title}</a></td>
                    <td><a href="#" onclick="javascript:addalbum({$RESULT.album_id});"><img src="/images/bullet_add.png" class="button" /></a> <a href="/details/album/{$RESULT.album_id}/">{$RESULT.album_name}</a></td>
                    <td align="right" nowrap>{$RESULT.duration|date_format:"%M:%S"} ({$RESULT.cost} <img src="/images/money.png" class="button" />)</td>
                  </tr>
                {/foreach}
                </table>
                <p align="center">{$LINKS}</p>
                {else}
                <p>no favorites found. please use the love &amp; hate icons next to the NOW PLAYING track.</p>
                {/if}
            
            </div>
