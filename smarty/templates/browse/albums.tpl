						<h1><a name="intro" id="intro"></a>Browse by albums</h1>

						<p>
            {foreach from=$ALPHA_INDEX item=ALPHA}
            <a href="/browse/albums/byalpha/{$ALPHA.alpha|lower}/">{$ALPHA.alpha}</a>&nbsp;&nbsp;
            {/foreach}
            </p>
            <div id="results">
            {foreach from=$ALBUMS item=ALBUM}
            <a href="/browse/albums/byid/{$ALBUM.album_id|lower}/">{$ALBUM.title}</a><br />
            {/foreach}
            </div>