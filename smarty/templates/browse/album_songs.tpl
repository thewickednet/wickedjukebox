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

            <h2>{$ALBUM.title}{if $PERMISSIONS.queue_add eq '1'} -<a href="#" onclick="javascript:addalbum({$ALBUM.album_id});"><img src="/images/add.gif" border="0" /></a>{/if}</h2>

            <table cellspacing="6" width="750">
            <tr>
              <td>Artist:</b> <a href="/browse/artist/byid/{$ARTIST.artist_id}/">{$ARTIST.name}</a></td>
              <td rowspan="4" align="right">
              {if $COVER ne ''}
              <img src="/browse/albums/cover/{$ALBUM.album_id}/" border="0" />
              {/if}
              </td>
            </tr>
            <tr>
              <td><b>Added to DB:</b> {$ALBUM.added|date_format:"%d.%m.%Y@%H:%M:%S"}</td>
            </tr>
            <tr>
              <td><b>Downloaded:</b> {$ALBUM.downloaded}</td>
            </tr>
            <tr>
              <td><a href="/download/album/{$ALBUM.album_id}/">Download Album</a></td>
            </tr>
            </table>

            <h3>Songs on this album</h3>
            <div id="results">
            <table cellspacing="6">
            {foreach from=$SONGS item=SONG}
              <tr>
                <td width="24">{if $PERMISSIONS.queue_add eq '1'}<a href="#" onclick="javascript:addsong({$SONG.song_id});"><img src="/images/add.gif" border="0" /></a>{/if}</td>
                <td>{$SONG.track_no} - <a href="/details/song/{$SONG.song_id}/">{$SONG.song}</a></td>
                <td align="right">{$SONG.duration|date_format:"%M:%S"}</td>
              </tr>
            {/foreach}
            </table>
            </div>
