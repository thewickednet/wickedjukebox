            <h1>Now Playing</h1>
            {if count($PLAYER_STATUS) ne '0'}
            {if $PLAYER_STATUS.cover ne ''}
            <a href="/browse/albums/byid/{$PLAYER_STATUS.song_info.album_id}/"><img src="/browse/albums/thumb/{$PLAYER_STATUS.song_info.album_id}/" border="0" id="img_queue"/></a>
            {/if}
            <p class="nowplaying"><a href="/details/song/{$PLAYER_STATUS.song_info.song_id}/">{$PLAYER_STATUS.song_info.name}<br />{$PLAYER_STATUS.song_info.title} ({$PLAYER_STATUS.song_info.duration|date_format:"%M:%S"})</a></p>
            {else}
            <p>Status: not available</p>
            {/if}

            <h1>Queue</h1>
            {if count($QUEUE) ne '0'}
            {foreach from=$QUEUE item=QUEUE_SONG}
			     <li><a href="/details/song/{$QUEUE_SONG.song_id}/">{$QUEUE_SONG.name} - {$QUEUE_SONG.title} ({$QUEUE_SONG.duration|date_format:"%M:%S"}) [{$QUEUE_SONG.fullname}]</a>{if $CORE->permissions.queue_remove eq '1' || $CORE->user_id eq $QUEUE_SONG.user_id}<a href="#" onclick="javascript:delsong({$QUEUE_SONG.queue_id});" style="color: red;"><img src="/images/bullet_delete.png" class="button" /></a>{/if}<br /></li>
            {/foreach}
                <li style="border-top: 1px solid #eeeeee; padding-top: 5px;">Total: {$QUEUE_TOTAL.totaltime|date_format:"%M:%S"}{if $CORE->permissions.admin eq '1'} - <a href="#" onclick="javascript:cleanqueue();" style="color: red;">clean queue</a>{/if}</li>
            {else}
            the queue is empty.
            {/if}
            <p><a href="#" onclick="javascript:refreshQueue();">refresh queue</a></p>