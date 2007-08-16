            <h1>Now Playing</h1>
            {if count($PLAYER_STATUS) ne '0'}
            {if $PLAYER_STATUS.cover ne ''}
            <a href="/browse/albums/byid/{$PLAYER_STATUS.song_info.album_id}/"><img src="/browse/albums/thumb/{$PLAYER_STATUS.song_info.album_id}/" border="0" id="img_queue"/></a>
            {/if}
            <p class="nowplaying">
            <a href="/details/song/{$PLAYER_STATUS.songinfo.id}/">
            <img src="/img.php?category=song&preset=queue&id={$PLAYER_STATUS.songinfo.id}" align="left" vspace="7" hspace="7" style="border: 1px solid #cccccc; background-color: #ffffff; padding: 3px; margin-right: 2px; margin-top: 3px;" />
            {$PLAYER_STATUS.artistinfo.name}<br />{$PLAYER_STATUS.songinfo.title}<br />({$PLAYER_STATUS.songinfo.duration|date_format:"%M:%S"})</a></p>
            <script>
            document.title = '{$PLAYER_STATUS.artistinfo.name|escape:javascript} - {$PLAYER_STATUS.songinfo.title|escape:javascript}' + ' is currently playing @ Wicked Jukebox';
            </script>
            {else}
            <p>Status: not available</p>
            <script>
            document.title = 'Wicked Jukebox';
            </script>
            {/if}
            <p>&nbsp;<br />&nbsp;</p>
            <h1>Queue</h1>
            {if count($QUEUE) ne '0'}
            <ul id="queue_list" {if $CORE->permissions.admin eq '1'}class="sortable-list"{/if}>
            {foreach from=$QUEUE item=QUEUE_SONG}
			     <li id="queue_{$QUEUE_SONG.queue_id}"><a href="/details/artist/{$QUEUE_SONG.artist_id}/">{$QUEUE_SONG.name|truncate:30}</a><br /><a href="/details/song/{$QUEUE_SONG.song_id}/">{$QUEUE_SONG.title|truncate:30}</a> ({$QUEUE_SONG.duration|date_format:"%M:%S"}) [{$QUEUE_SONG.fullname}]{if $CORE->permissions.queue_remove eq '1' || $CORE->user_id eq $QUEUE_SONG.user_id}<a href="#" onclick="javascript:delsong({$QUEUE_SONG.queue_id});" style="color: red;"><img src="/images/bullet_delete.png" class="button" /></a>{/if}<br /></li>
            {/foreach}
            </ul>
                <li style="border-bottom: 0px solid #eeeeee; padding-top: 5px;"><b>Total:</b> {$QUEUE_TOTAL.totaltime|date_format:"%M:%S"}{if $CORE->permissions.admin eq '1'} - <a href="#" onclick="javascript:cleanqueue();" style="color: red;">clean queue</a>{/if}</li>

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
            
            <p><a href="#" onclick="javascript:refreshQueue();">refresh queue</a></p>
