
						<h1><a name="intro" id="intro"></a>100 Latest Additions</h1>

            <div id="results">

                {if count($RESULTS) ne '0'}
                <table cellspacing="1" cellpadding="4">
                {foreach from=$RESULTS item=RESULT}
                  <tr class="resultlist">
                    <td nowrap><a href="/artist/detail/{$RESULT.artist_id}/">{$RESULT.artist_name}</a></td>
                    <td><a href="javascript:;" onclick="javascript:addsong({$RESULT.song_id});"><img src="/images/bullet_add.png" class="button" /></a> <a href="/song/detail/{$RESULT.song_id}/">{$RESULT.song_title}</a></td>
                    <td><a href="javascript:;" onclick="javascript:addalbum({$RESULT.album_id});"><img src="/images/bullet_add.png" class="button" /></a> <a href="/album/detail/{$RESULT.album_id}/">{$RESULT.album_name}</a></td>
                    <td align="right" nowrap>{$RESULT.added|date_format:"%d.%m.%Y@%H:%M:%S"}</td>
                  </tr>
                {/foreach}
                </table>
                {else}
                <p>no results found</p>
                {/if}
            
            
            </div>
