<h1>Now Playing</h1>

            {if count($PLAYER_STATUS) ne '0'}

            <p class="now">
            <img src="/img.php?category=song&preset=splash&id={$PLAYER_STATUS.songinfo.id}" id="coverart" align="left" />
            <a href="/song/detail/{$PLAYER_STATUS.songinfo.id}/">
            {$PLAYER_STATUS.songinfo.title}</a><br />
            by <a href="/artist/detail/{$PLAYER_STATUS.artistinfo.id}/">{$PLAYER_STATUS.artistinfo.name}</a><br />
            {if $PLAYER_STATUS.albuminfo.id ne ''}
            on <a href="/album/detail/{$PLAYER_STATUS.albuminfo.id}/">{$PLAYER_STATUS.albuminfo.name}</a><br />
            {else}
            &nbsp;<br />
            {/if}
            {$PLAYER_STATUS.progress|date_format:"%M:%S"} / {$PLAYER_STATUS.songinfo.duration|date_format:"%M:%S"}
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            <a href="javascript:;" onclick="javascript:setStanding({$PLAYER_STATUS.songinfo.id}, 'love', 'splash');"><img src="/images/emoticon_happy.png" title="love this track!" border="0" class="icon{if $PLAYER_STATUS.standing == 'love'}a{/if}"/></a>&nbsp;<a href="javascript:;" onclick="javascript:setStanding({$PLAYER_STATUS.songinfo.id}, 'neutral', 'splash');"><img src="/images/emoticon_smile.png" title="this track is ok!" border="0" class="icon{if $PLAYER_STATUS.standing != 'love' && $PLAYER_STATUS.standing != 'hate'}a{/if}"/></a>&nbsp;<a href="javascript:;" onclick="javascript:setStanding({$PLAYER_STATUS.songinfo.id}, 'hate', 'splash');"><img src="/images/emoticon_unhappy.png" title="hate this track!" border="0" class="icon{if $PLAYER_STATUS.standing == 'hate'}a{/if}"/></a>&nbsp;<a href="javascript:;" onclick="javascript:setStanding({$PLAYER_STATUS.songinfo.id}, 'broken', 'splash');"><img src="/images/error.png" title="report track as broken or very bad quality" border="0" class="icon" /></a>
            </p>
            <p>
            Loved: 
            {if $PLAYER_STATUS.standings.love_count > 0}
                <a href="javascript:void(0);" onmouseover="return overlib('Users who love this song:<br>{foreach from=$PLAYER_STATUS.standings.love item=LOVE_ITEM}{$LOVE_ITEM.fullname}<br>{/foreach}');" onmouseout="return nd();">{$PLAYER_STATUS.standings.love_count}</a>
            {else}
                {$PLAYER_STATUS.standings.love_count}
            {/if}
            /
            Hated: 
            {if $PLAYER_STATUS.standings.hate_count > 0}
                <a href="javascript:void(0);" onmouseover="return overlib('Users who hate this song:<br>{foreach from=$PLAYER_STATUS.standings.hate item=HATE_ITEM}{$HATE_ITEM.fullname}<br>{/foreach}');" onmouseout="return nd();">{$PLAYER_STATUS.standings.hate_count}</a>
            {else}
                {$PLAYER_STATUS.standings.hate_count}
            {/if}
            </p>
            <script>
            document.title = '{$PLAYER_STATUS.songinfo.title|escape:javascript} by {$PLAYER_STATUS.artistinfo.name|escape:javascript}' + ' is currently playing @ Wicked Jukebox';
            </script>

            {else}
            <p>Status: not available</p>
            <script>
            document.title = 'Wicked Jukebox';
            </script>
            {/if}
