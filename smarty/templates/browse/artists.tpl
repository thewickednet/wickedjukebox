						<h1><a name="intro" id="intro"></a>Browse by artists</h1>

						<p>
            {foreach from=$ALPHA_INDEX item=ALPHA}
            <a href="/browse/artists/byalpha/{$ALPHA.alpha|lower}/">{$ALPHA.alpha}</a>&nbsp;&nbsp;
            {/foreach}
            </p>
            <div id="results">
            {foreach from=$ARTISTS item=ARTIST}
            <a href="/browse/artists/byid/{$ARTIST.artist_id|lower}/">{$ARTIST.name}</a><br />
            {/foreach}
            </div>