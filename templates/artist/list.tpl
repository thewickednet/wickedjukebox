						<h1><a name="intro" id="intro"></a>Browse by artists</h1>

						{include file='artist/alpha_index.tpl'}

            <div id="results">
            {foreach from=$ARTISTS item=ARTIST}
            <a href="/details/artist/{$ARTIST.id|lower}/">{$ARTIST.name}</a><br />
            {/foreach}
            </div>
