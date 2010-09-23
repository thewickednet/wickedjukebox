                <p align="center">{$LINKS}</p>
                <table cellspacing="1" cellpadding="4">
                {foreach from=$RESULTS item=RESULT}
                  <tr class="resultlist">
                    <td><a href="/artists/detail/{$RESULT.artist_id}/">{$RESULT.artist_name}</a></td>
                    <td><a href="javascript:;" onclick="javascript:addsong({$RESULT.song_id});"><img src="/images/bullet_add.png" class="button" /></a> <a href="/song/detail/{$RESULT.song_id}/">{$RESULT.song_title}</a></td>
                    {if $RESULT.album_name ne ''}
                    <td><a href="javascript:;" onclick="javascript:addalbum({$RESULT.album_id});"><img src="/images/bullet_add.png" class="button" /></a> <a href="/album/detail/{$RESULT.album_id}/">{highLight string=$RESULT.album_name mask=$SEARCH_PATTERN}</a></td>
                    {else}
                    <td>&nbsp;</td>
                    {/if}
                  </tr>
                {/foreach}
                </table>
                <p align="center">{$LINKS}</p>
