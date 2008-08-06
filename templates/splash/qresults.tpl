           <ul id="qresult_list">
    {foreach from=$QRESULTS item=QRESULT}
	     <li {if $QRESULT.standing ne ''}class="{$QRESULT.standing}"{/if}><a href="/song/detail/{$QRESULT.song_id}/">{$QRESULT.song_name|truncate:30}</a>{if $CORE->permissions.queue_add eq '1'}<a href="javascript:;" onclick="javascript:addsplashsong({$QRESULT.song_id});"><img src="/images/bullet_add.png" class="button" align="right" /></a>{/if}<br />by <a href="/artist/detail/{$QRESULT.artist_id}/">{$QRESULT.artist_name|truncate:30}</a> ({$QRESULT.duration|date_format:"%M:%S"})</li>
    {/foreach}
            </ul>            
            
