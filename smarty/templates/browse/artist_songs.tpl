
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
            <h2>{$ARTIST.name}</h2>


            {if $ARTIST.name eq 'Various Artists' || $ARTIST.name eq 'Soundtracks' || $ARTIST.name eq 'Video Games'}
            <h3>Songs in this category</h3>
            {else}
            {if $COVER ne ''}
              <img src="/browse/artists/cover/{$ARTIST.artist_id}/" border="0" id="img_artist" />
            <h3>Songs by this artist</h3>
            {/if}
	    {/if}
            <div id="results">
            <table>
            {foreach from=$SONGS item=SONG}
              <tr>
                <td width="24">{if $PERMISSIONS.queue_add eq '1'}<a href="#" onclick="javascript:addsong({$SONG.song_id});"><img src="/images/add.gif" border="0" /></a>{/if}</td>
                <td><a href="/details/song/{$SONG.song_id}/">{$SONG.song}</a></td>
                <td width="24">{if $PERMISSIONS.queue_add eq '1'}<a href="#" onclick="javascript:addalbum({$SONG.album_id});"><img src="/images/add_album.gif" border="0" /></a>{/if}</td>
                <td><a href="/browse/albums/byid/{$SONG.album_id}/">{$SONG.album}</a></td>
                <td align="right">{$SONG.duration|date_format:"%M:%S"}</td>
              </tr>
            {/foreach}
            <tr>
            <td colspan="5" align="center">{$LINKS}</td>
            </tr>
            </table>
            </div>
