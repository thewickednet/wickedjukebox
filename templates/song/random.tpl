            <br />
            <h1>Teh random pickr</h1>
            {if count($RANDOM_SONGS) ne '0'}
            <ul id="random_list">
            {foreach from=$RANDOM_SONGS item=RANDOM_SONG}
			     <li {if $RANDOM_SONG.standing ne ''}class="{$RANDOM_SONG.standing}"{/if}><a href="/song/detail/{$RANDOM_SONG.song_id}/">{$RANDOM_SONG.title|truncate:30}</a>{if $CORE->permissions.queue_add eq '1'}<a href="javascript:;" onclick="javascript:addsong({$RANDOM_SONG.song_id});"><img src="/images/bullet_add.png" class="button" align="right" /></a>{/if}<br />by <a href="/artist/detail/{$RANDOM_SONG.artist_id}/">{$RANDOM_SONG.artist_name|truncate:30}</a> ({$RANDOM_SONG.duration|date_format:"%M:%S"}) {*{$RANDOM_SONG.cost}cr *}</li>
            {/foreach}
            </ul>
    
            {else}
            no suggestions available
            {/if}
            
            <p><a href="javascript:;" onclick="javascript:refreshRandom('sidebar');">gimme more...</a><img src="/images/carousel.gif" align="right" style="display:none;" id="random_carousel" /><br /></p>
