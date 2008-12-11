            <p align="center">{$LINKS}</p>
            <table>
            {foreach from=$SONGS item=SONG}
              <tr {if $SONG.standing ne ''}class="{$SONG.standing}"{/if}>
                <td width="24">{if $CORE->permissions.queue_add eq '1'}<a href="javascript:;" onclick="javascript:addsong({$SONG.song_id});"><img src="/images/bullet_add.png" class="button" /></a>{/if}</td>
                <td><a href="/song/detail/{$SONG.song_id}/">{$SONG.title}</a></td>
                <td width="24">{if $CORE->permissions.queue_add eq '1'}<a href="javascript:;" onclick="javascript:addalbum({$SONG.album_id});"><img src="/images/bullet_add.png" class="button" /></a>{/if}</td>
                <td><a href="/album/detail/{$SONG.album_id}/">{$SONG.album_name}</a></td>
                <td align="right">{$SONG.duration|date_format:"%M:%S"} ({$SONG.cost} <img src="/images/money.png" class="button" />)</td>
              </tr>
            {/foreach}
            <tr>
            <td colspan="5" align="center">{$LINKS}</td>
            </tr>
            </table>
