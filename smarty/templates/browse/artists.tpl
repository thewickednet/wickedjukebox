						<h1><a name="intro" id="intro"></a>Browse by artists</h1>

						<p>
            <a href="/browse/artists/byalpha/num/">0-9</a> -
            <a href="/browse/artists/byalpha/a/">A</a> -
            <a href="/browse/artists/byalpha/b/">B</a> -
            <a href="/browse/artists/byalpha/c/">C</a> -
            <a href="/browse/artists/byalpha/d/">D</a> -
            <a href="/browse/artists/byalpha/e/">E</a> -
            <a href="/browse/artists/byalpha/f/">F</a> -
            <a href="/browse/artists/byalpha/g/">G</a> -
            <a href="/browse/artists/byalpha/h/">H</a> -
            <a href="/browse/artists/byalpha/i/">I</a> -
            <a href="/browse/artists/byalpha/j/">J</a> -
            <a href="/browse/artists/byalpha/k/">K</a> -
            <a href="/browse/artists/byalpha/l/">L</a> -
            <a href="/browse/artists/byalpha/m/">M</a> -
            <a href="/browse/artists/byalpha/n/">N</a> -
            <a href="/browse/artists/byalpha/o/">O</a> -
            <a href="/browse/artists/byalpha/p/">P</a> -
            <a href="/browse/artists/byalpha/q/">Q</a> -
            <a href="/browse/artists/byalpha/r/">R</a> -
            <a href="/browse/artists/byalpha/s/">S</a> -
            <a href="/browse/artists/byalpha/t/">T</a> -
            <a href="/browse/artists/byalpha/u/">U</a> -
            <a href="/browse/artists/byalpha/v/">V</a> -
            <a href="/browse/artists/byalpha/w/">W</a> -
            <a href="/browse/artists/byalpha/x/">X</a> -
            <a href="/browse/artists/byalpha/y/">Y</a> -
            <a href="/browse/artists/byalpha/z/">Z</a><br />
            <a href="/browse/artists/byalpha/various/">Various</a> -
            <a href="/browse/artists/byalpha/ost/">Soundtrack</a> -
            <a href="/browse/artists/byalpha/videogame/">Video Games</a>
            </p>
            <div id="results">
            {foreach from=$ARTISTS item=ARTIST}
            <a href="/browse/artists/byid/{$ARTIST.artist_id|lower}/">{$ARTIST.name}</a><br />
            {/foreach}
            </div>