
						<h1><a name="intro" id="intro"></a>100 Latest Additions</h1>

            <div id="results">

                {if count($RESULTS) ne '0'}
                {foreach from=$RESULTS item=RESULT}
                {assign var="date_formatted" value=$RESULT.added|date_format:"%A, %B %e, %Y"}
                {if $date_formatted ne $date_list}
                {assign var="date_list" value=$date_formatted}
                <h2>{$date_list}</h2>
                {/if}
                <a href="/album/detail/{$RESULT.album_id}/"><img src="/img.php?category=album&preset=latest&id={$RESULT.album_id}" style="border: 1px solid #cccccc; background-color: #ffffff; padding: 3px; margin-right: 2px; margin-top: 3px;" id="img_artist" title='{$RESULT.artist_name} - {$RESULT.album_name}'></a>
                {/foreach}
                {else}
                <p>no results found</p>
                {/if}
            
            
            </div>
