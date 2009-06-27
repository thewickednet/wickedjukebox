
						<h1><a name="intro" id="intro"></a>Search</h1>

            <h2>You were looking for "{$SEARCH_PATTERN}" in "{$SEARCH_MODE}"</h2>

            <h3>Results ({$RESULT_COUNT} matches found)</h3>
            <div id="results">
            {if $ERROR_MESSAGE ne ''}
                <p><img src="/images/exclamation.png" /> {$ERROR_MESSAGE}</p>
            {else}
            

                {if count($RESULTS) ne '0'}
                <p align="center">{$LINKS}</p>
                <table cellspacing="1" cellpadding="4">
                {foreach from=$RESULTS item=RESULT}
                  <tr {if $RESULT.standing ne ''}class="{$RESULT.standing} resultlist"{else}class="resultlist"{/if}>
                    <td><a href="/artist/detail/{$RESULT.artist_id}/">{highLight string=$RESULT.artist_name mask=$SEARCH_PATTERN}</a></td>
                    <td><a href="javascript:;" onclick="javascript:addsong({$RESULT.song_id});"><img src="/images/bullet_add.png" class="button" /></a> <a href="/song/detail/{$RESULT.song_id}/">{highLight string=$RESULT.song_name mask=$SEARCH_PATTERN}</a></td>
                    {if $RESULT.album_name ne ''}
                    <td><a href="javascript:;" onclick="javascript:addalbum({$RESULT.album_id});"><img src="/images/bullet_add.png" class="button" /></a> <a href="/album/detail/{$RESULT.album_id}/">{highLight string=$RESULT.album_name mask=$SEARCH_PATTERN}</a></td>
                    {else}
                    <td>&nbsp;</td>
                    {/if}
                    <td align="right" nowrap>{$RESULT.duration|date_format:"%M:%S"} ({$RESULT.cost} <img src="/images/money.png" class="button" />)</td>
                    <td align="right" nowrap>{$RESULT.orating}</td>
                  </tr>
                {/foreach}
                </table>
                <p align="center">{$LINKS}</p>
                {else}
                <p>no results found</p>
                {/if}
            
            
            {/if}
            
            
            </div>
