						{if count($PLAYER_STATUS) ne '0'}
            <p><b>Status:</b> {$PLAYER_STATUS.status}<br />
						<a href="/details/song/{$PLAYER_STATUS.song_id}/">{$PLAYER_STATUS.name} - {$PLAYER_STATUS.title} ({$PLAYER_STATUS.duration|date_format:"%M:%S"})
						</p>
						{else}
						<p>Status: not available</p>
						{/if}
						<hr size="1" noshade>
            {if count($QUEUE) ne '0'}
            {foreach from=$QUEUE item=QUEUE_SONG}
								<li><a href="/details/song/{$QUEUE_SONG.song_id}/">{$QUEUE_SONG.name} - {$QUEUE_SONG.title} ({$QUEUE_SONG.duration|date_format:"%M:%S"}) [{$QUEUE_SONG.fullname}]</a>{if $PERMISSIONS.queue_remove eq '1'}<a href="#" onclick="javascript:delsong({$QUEUE_SONG.queue_id});" style="color: red;"> del</a>{/if}<br /></li>
            {/foreach}
                <li style="border-top: 1px solid #eeeeee; padding-top: 5px;">Total: {$QUEUE_TOTAL.total_time}{if $PERMISSIONS.admin eq '1'} - <a href="#" onclick="javascript:cleanqueue();" style="color: red;">clean</a>{/if}</li>
            {else}
            the queue is empty.
            {/if}
