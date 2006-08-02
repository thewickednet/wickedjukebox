            <h1>Now Playing</h1>
            {if count($PLAYER_STATUS) ne '0'}
            {if $PLAYER_STATUS.cover ne ''}
            <a href="/browse/albums/byid/{$PLAYER_STATUS.song_info.album_id}/"><img src="/images/indicator.gif" border="0" id="img_queue"/></a>
{literal}
<script language="Javascript">

  var timg_queue = new Image();
  timg_queue.onload = function () { loaded('queue', '/browse/albums/thumb/{/literal}{$PLAYER_STATUS.song_info.album_id}{literal}/'); } ;
  timg_queue.src = '/browse/albums/thumb/{/literal}{$PLAYER_STATUS.song_info.album_id}{literal}/';

</script>
{/literal}
            {/if}
            <p class="nowplaying"><a href="/details/song/{$PLAYER_STATUS.song_id}/">{$PLAYER_STATUS.song_info.name}<br />{$PLAYER_STATUS.song_info.title} ({$PLAYER_STATUS.song_info.duration|date_format:"%M:%S"})</a></p>
            {else}
            <p>Status: not available</p>
            {/if}

            <h1>Queue</h1>
            {if count($QUEUE) ne '0'}
            {foreach from=$QUEUE item=QUEUE_SONG}
								<li><a href="/details/song/{$QUEUE_SONG.song_id}/">{$QUEUE_SONG.name} - {$QUEUE_SONG.title} ({$QUEUE_SONG.duration|date_format:"%M:%S"}) [{$QUEUE_SONG.fullname}]</a>{if $PERMISSIONS.queue_remove eq '1'}<a href="#" onclick="javascript:delsong({$QUEUE_SONG.queue_id});" style="color: red;"> del</a>{/if}<br /></li>
            {/foreach}
                <li style="border-top: 1px solid #eeeeee; padding-top: 5px;">Total: {$QUEUE_TOTAL.total_time}{if $PERMISSIONS.admin eq '1'} - <a href="#" onclick="javascript:cleanqueue();" style="color: red;">clean</a>{/if}</li>
            {else}
            the queue is empty.
            {/if}
