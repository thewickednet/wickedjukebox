						{if count($QUEUE) ne '0'}
            {foreach from=$QUEUE item=QUEUE_SONG}
								<li><a href="/details/song/{$QUEUE_SONG.song_id}/">{$QUEUE_SONG.name} - {$QUEUE_SONG.title} ({$QUEUE_SONG.duration|date_format:"%M:%S"})</a> - <a href="#" onclick="javascript:delsong({$QUEUE_SONG.queue_id});" style="color: red;">del</a><br /></li>
            {/foreach}
                <li style="border-top: 1px solid #eeeeee; padding-top: 5px;">Total: {$QUEUE_TOTAL.total_time} - <a href="#" onclick="javascript:cleanqueue();" style="color: red;">clean</a></li>
            {else}
            the queue is empty.
            {/if}
