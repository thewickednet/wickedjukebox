<h1>Now Playing<div style="float: right; padding-right: 50px;"><a href="javascript:;" onclick="javascript:setStanding({$PLAYER_STATUS.songinfo.id}, 'love', 'splash');"><img src="/images/emoticon_happy.png" title="love this track!" border="0" class="icon{if $PLAYER_STATUS.standing == 'love'}a{/if}"/></a>&nbsp;<a href="javascript:;" onclick="javascript:setStanding({$PLAYER_STATUS.songinfo.id}, 'neutral', 'splash');"><img src="/images/emoticon_smile.png" title="this track is ok!" border="0" class="icon{if $PLAYER_STATUS.standing != 'love' && $PLAYER_STATUS.standing != 'hate'}a{/if}"/></a>&nbsp;<a href="javascript:;" onclick="javascript:setStanding({$PLAYER_STATUS.songinfo.id}, 'hate', 'splash');"><img src="/images/emoticon_unhappy.png" title="sorry, not for me!" border="0" class="icon{if $PLAYER_STATUS.standing == 'hate'}a{/if}"/></a>&nbsp;<a href="javascript:;" onclick="javascript:setStanding({$PLAYER_STATUS.songinfo.id}, 'broken', 'splash');"><img src="/images/error.png" title="report track as broken or very bad quality" border="0" class="icon" /></a></div></h1>

            {if count($PLAYER_STATUS) ne '0'}

            <div id="coverslide">
            <img src="/img.php?category=song&preset=splash&id={$PLAYER_STATUS.songinfo.id}" id="coverart" class="active" align="left" title="{$PLAYER_STATUS.albuminfo.name}" />
            <img src="/img.php?category=artist&preset=splash&id={$PLAYER_STATUS.artistinfo.id}" id="coverart" align="left" title="{$PLAYER_STATUS.artistinfo.name}" />
            </div>

            <div id="coverinfo">
            <p class="now">
            <a href="/song/detail/{$PLAYER_STATUS.songinfo.id}/">
            {$PLAYER_STATUS.songinfo.title}</a><br />
            by <a href="/artist/detail/{$PLAYER_STATUS.artistinfo.id}/">{$PLAYER_STATUS.artistinfo.name}</a><br />
            {if $PLAYER_STATUS.albuminfo.name ne ''}
            on <a href="/album/detail/{$PLAYER_STATUS.albuminfo.id}/">{$PLAYER_STATUS.albuminfo.name}</a> {if $PLAYER_STATUS.albuminfo.release_date ne ''}({$PLAYER_STATUS.albuminfo.release_date|date_format:"%Y"}){/if}
            {else}
            &nbsp;
            {/if}
            </p>
{*
step: {$PLAYER_STATUS.step} / 
duration: {$PLAYER_STATUS.songinfo.duration} / 
state: {$PLAYER_STATUS.state.progress}
*}
            <div id="bardivs">
                <div id="progressbar"></div>
                <div id="progress"><span name="counter" sec="{$PLAYER_STATUS.progress}" inc="1" max="{$PLAYER_STATUS.songinfo.duration}">{$PLAYER_STATUS.progress|date_format:"%M:%S"}</span></div>
                <div id="duration">{$PLAYER_STATUS.songinfo.duration|date_format:"%M:%S"}</div>
            </div>
            <!--
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
            -->
            <script>
            document.title = '{$PLAYER_STATUS.songinfo.title|escape:javascript} by {$PLAYER_STATUS.artistinfo.name|escape:javascript}' + ' is currently playing @ Wicked Jukebox';
            </script>

            {else}
            
            <p>Status: not available</p>
            <script>
            document.title = 'Wicked Jukebox';
            </script>
            
            {/if}

			{if count($QUEUE) ne '0'}
            {* @doc: first! :P *}
            <p><strong>Coming up:</strong> <a href="/song/detail/{$QUEUE[0].song_id}/">{$QUEUE[0].artist_name} - {$QUEUE[0].title}</a> ({$QUEUE[0].duration|date_format:"%M:%S"}) [{$QUEUE[0].fullname}]</p>
			{elseif $PLAYER_STATUS.nextsong.id ne ''}
            <p><strong>Coming up:</strong> <a href="/song/detail/{$PLAYER_STATUS.nextsong.id}/">{$PLAYER_STATUS.nextartist.name} - {$PLAYER_STATUS.nextsong.title}</a> ({$PLAYER_STATUS.nextsong.duration|date_format:"%M:%S"}) [random]</p>
            {/if}
            </div>
            
{literal}
          <script>  
              
$(document).ready(function() { 
	$('#coverslide').innerfade({ 
		speed: 'slow', 
		timeout: 5000,
		type: 'sequence'
	});

{/literal}

    $.doTimeout('counter', 1000, function(){ldelim}

        var progress = $("#progressbar").progressbar("value");

        $("#progressbar").progressbar( "value" , progress + {$PLAYER_STATUS.step} );

        counter();
        return true;
    {rdelim});

    $("#progressbar").progressbar({ldelim} value: {$PLAYER_STATUS.state.progress} {rdelim});
});



</script>

            
