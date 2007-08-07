						<h1><a name="intro" id="intro"></a>Browse by albums</h1>

						{include file='album/alpha_index.tpl'}

            <div id="results">
            {foreach from=$ALBUMS item=ALBUM}
            <a href="/detail/album/{$ALBUM.album_id}/">{$ALBUM.album_name}</a><br />
            {/foreach}
            </div>
           