            {if $MESSAGE ne '' && $MESSAGE ne 'UPDATE_PROFILE'}
            <script>
            alert('{$MESSAGE|escape:'javascript'}');
            </script>
            {/if}
            <h1>Now Playing</h1>
            {if count($PLAYER_STATUS) ne '0'}
            {if $PLAYER_STATUS.cover ne ''}
            <a href="/browse/albums/byid/{$PLAYER_STATUS.song_info.album_id}/"><img src="/browse/albums/thumb/{$PLAYER_STATUS.song_info.album_id}/" border="0" id="img_queue"/></a>
            {/if}
            <p class="nowplaying">
            <a href="/details/song/{$PLAYER_STATUS.songinfo.id}/">
            <img src="/img.php?category=song&preset=queue&id={$PLAYER_STATUS.songinfo.id}" align="left" vspace="7" hspace="7" style="border: 1px solid #cccccc; background-color: #ffffff; padding: 3px; margin-right: 8px; margin-top: 0" />
            {$PLAYER_STATUS.songinfo.title}</a><br />by <a href="/details/artist/{$PLAYER_STATUS.artistinfo.id}/">{$PLAYER_STATUS.artistinfo.name}</a><br />({$PLAYER_STATUS.songinfo.duration|date_format:"%M:%S"})</a></p>
            
            <!--[queued by {$PLAYER_STATUS.userinfo.fullname}]-->
            {if $CORE->user_id ne '-1'}
            <a href="javascript:;" onclick="javascript:setStanding({$PLAYER_STATUS.songinfo.id}, 'love');"><img src="/images/emoticon_happy.png" title="love this track!" border="0" class="icon{if $PLAYER_STATUS.standing == 'love'}a{/if}"/></a>&nbsp;<a href="javascript:;" onclick="javascript:setStanding({$PLAYER_STATUS.songinfo.id}, 'neutral');"><img src="/images/emoticon_smile.png" title="this track is ok!" border="0" class="icon{if $PLAYER_STATUS.standing != 'love' && $PLAYER_STATUS.standing != 'hate'}a{/if}"/></a>&nbsp;<a href="javascript:;" onclick="javascript:setStanding({$PLAYER_STATUS.songinfo.id}, 'hate');"><img src="/images/emoticon_unhappy.png" title="hate this track!" border="0" class="icon{if $PLAYER_STATUS.standing == 'hate'}a{/if}"/></a>&nbsp;<a href="javascript:;" onclick="javascript:setStanding({$PLAYER_STATUS.songinfo.id}, 'broken');"><img src="/images/error.png" title="report track as broken or very bad quality" border="0" class="icon" /></a>
            {/if}
            <script>
            document.title = '{$PLAYER_STATUS.songinfo.title|escape:javascript} by {$PLAYER_STATUS.artistinfo.name|escape:javascript}' + ' is currently playing @ Wicked Jukebox';
            </script>
            {else}
            <p>Status: not available</p>
            <script>
            document.title = 'Wicked Jukebox';
            </script>
            {/if}
            <p>Radio users connected: {$ICECAST.0->listeners}<br />
            Website users connected:{$ALIVE_USERS_COUNT}</p>
            {if count($ALIVE_USERS) > 0}
            <p>
            {foreach name="ulist" from=$ALIVE_USERS item=ALIVE_USER}
            <a href="/?module=user&action=detail&id={$ALIVE_USER.id}"><img src="/img.php?category=user&preset=icon&id={$ALIVE_USER.id}" style="border: 1px solid #cccccc; background-color: #ffffff; padding: 3px; margin-right: 2px; margin-top: 3px;" id="img_album" title="{$ALIVE_USER.fullname}"/></a>&nbsp;
            {/foreach}
            </p>
            {else}
            <p>no user online</p>
            {/if}
            <h1>Queue</h1>
            {if count($QUEUE) ne '0'}
            <ul id="queue_list" {if $CORE->permissions.admin eq '1'}class="sortable-list"{/if}>
            {foreach from=$QUEUE item=QUEUE_SONG}
			     <li id="queue_{$QUEUE_SONG.queue_id}"><a href="/details/song/{$QUEUE_SONG.song_id}/">{$QUEUE_SONG.title|truncate:30}</a><br />by <a href="/details/artist/{$QUEUE_SONG.artist_id}/">{$QUEUE_SONG.artist_name|truncate:30}</a> ({$QUEUE_SONG.duration|date_format:"%M:%S"}) [{$QUEUE_SONG.fullname}]{if $CORE->permissions.queue_remove eq '1' || $CORE->user_id eq $QUEUE_SONG.user_id}<a href="javascript:;" onclick="javascript:delsong({$QUEUE_SONG.queue_id});" style="color: red;"><img src="/images/bullet_delete.png" class="button" /></a>{/if}</li>
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
            
            <p><a href="javascript:;" onclick="javascript:refreshQueue();">refresh queue</a></p>
            {if $CORE->user_id ne '-1'}
            <script>
                refreshProfile();
            </script>
            {/if}
