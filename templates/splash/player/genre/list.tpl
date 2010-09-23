						<h1><a name="intro" id="intro"></a>Browse by genre</h1>

            <div id="results">
            {foreach from=$GENRES item=GENRE}
            <a href="/browse/genres/byid/{$GENRE.genre_id|lower}/">{$GENRE.name}</a><br />
            {/foreach}
            </div>