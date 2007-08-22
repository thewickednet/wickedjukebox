            <br />
            <h1>Teh random pickr</h1>
            {if count($RANDOM_SONGS) ne '0'}
            <ul id="random_list">
            {foreach from=$RANDOM_SONGS item=RANDOM_SONG}
			     <li><a href="/details/artist/{$RANDOM_SONG.artist_id}/">{$RANDOM_SONG.artist_name|truncate:30}</a><br /><a href="/details/song/{$RANDOM_SONG.song_id}/">{$RANDOM_SONG.title|truncate:30}</a> ({$RANDOM_SONG.duration|date_format:"%M:%S"}) {$RANDOM_SONG.cost}cr {if $CORE->permissions.queue_add eq '1'}<a href="javascript:;" onclick="javascript:addsong({$RANDOM_SONG.song_id});"><img src="/images/bullet_add.png" class="button" /></a>{/if}</li>
            {/foreach}
            </ul>
    
            {else}
            no suggestions available
            {/if}
            
            <p><a href="javascript:;" onclick="javascript:refreshRandom();">gimme more...</a><img src="/images/carousel.gif" align="right" style="display:none;" id="random_carousel" /><br /></p>