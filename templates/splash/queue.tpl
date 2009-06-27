
            <h1>Queue</h1>
            {if count($QUEUE) ne '0'}
            <ul id="queue_list" {if $CORE->permissions.admin eq '1'}class="sortable-list"{/if}>
            {foreach from=$QUEUE item=QUEUE_SONG}
			     <li id="queue_{$QUEUE_SONG.queue_id}" {if $QUEUE_SONG.standing ne ''}class="{$QUEUE_SONG.standing}"{/if}>
			     <img src="/img.php?category=song&preset=tiny&id={$QUEUE_SONG.song_id}" id="tinyart" align="left" /><a href="/song/detail/{$QUEUE_SONG.song_id}/">{$QUEUE_SONG.title|truncate:30}</a>{if $CORE->permissions.queue_remove eq '1' || $CORE->user_id eq $QUEUE_SONG.user_id}<a href="javascript:;" onclick="javascript:delsong({$QUEUE_SONG.queue_id});" style="color: red;"><img src="/images/bullet_delete.png" class="button" align="right" /></a>{/if} ({$QUEUE_SONG.duration|date_format:"%M:%S"})<br />by <a href="/artist/detail/{$QUEUE_SONG.artist_id}/">{$QUEUE_SONG.artist_name|truncate:30}</a> [{$QUEUE_SONG.fullname}]</li>
            {/foreach}
            </ul>
                <li style="border-bottom: 0px solid #eeeeee; padding-top: 5px;"><b>Total:</b> {$QUEUE_TOTAL.totaltime|date_format:"%M:%S"}{if $CORE->permissions.queue_remove eq '1' || $CORE->permissions.admin eq '1'} - <a href="javascript:;" onclick="javascript:cleanqueue();" style="color: red;">clean queue</a>{/if}</li>

            {if $CORE->permissions.admin eq '1'}
            {literal}
            <script type="text/javascript">
                Sortable.create('queue_list', { onUpdate : resortQueue });
            </script>
            {/literal}
            {/if}

            {else}
            the queue is empty.
            {/if}

            <p><a href="javascript:;" onclick="javascript:refreshQueue('sidebar');"><img src="/images/arrow_rotate_clockwise.png" border="0" title="refresh" /></a></p>
            {if $CORE->user_id ne '-1'}
            <script>
                refreshProfile('splash');
            </script>
            {/if}
