						<h1><a name="intro" id="intro"></a>Browse by albums</h1>

						<p>
            <a href="/browse/albums/byalpha/num/">0-9</a> -
            <a href="/browse/albums/byalpha/a/">A</a> -
            <a href="/browse/albums/byalpha/b/">B</a> -
            <a href="/browse/albums/byalpha/c/">C</a> -
            <a href="/browse/albums/byalpha/d/">D</a> -
            <a href="/browse/albums/byalpha/e/">E</a> -
            <a href="/browse/albums/byalpha/f/">F</a> -
            <a href="/browse/albums/byalpha/g/">G</a> -
            <a href="/browse/albums/byalpha/h/">H</a> -
            <a href="/browse/albums/byalpha/i/">I</a> -
            <a href="/browse/albums/byalpha/j/">J</a> -
            <a href="/browse/albums/byalpha/k/">K</a> -
            <a href="/browse/albums/byalpha/l/">L</a> -
            <a href="/browse/albums/byalpha/m/">M</a> -
            <a href="/browse/albums/byalpha/n/">N</a> -
            <a href="/browse/albums/byalpha/o/">O</a> -
            <a href="/browse/albums/byalpha/p/">P</a> -
            <a href="/browse/albums/byalpha/q/">Q</a> -
            <a href="/browse/albums/byalpha/r/">R</a> -
            <a href="/browse/albums/byalpha/s/">S</a> -
            <a href="/browse/albums/byalpha/t/">T</a> -
            <a href="/browse/albums/byalpha/u/">U</a> -
            <a href="/browse/albums/byalpha/v/">V</a> -
            <a href="/browse/albums/byalpha/w/">W</a> -
            <a href="/browse/albums/byalpha/x/">X</a> -
            <a href="/browse/albums/byalpha/y/">Y</a> -
            <a href="/browse/albums/byalpha/z/">Z</a>
            </p>
            <div id="results">
            {foreach from=$ALBUMS item=ALBUM}
            <a href="/browse/albums/byid/{$ALBUM.album_id|lower}/">{$ALBUM.title}</a><br />
            {/foreach}
            </div>