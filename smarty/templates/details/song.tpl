						<h1><a name="intro" id="intro"></a>Song Details</h1>

            <h2>{$SONG.title}&nbsp;&nbsp;<a href="#" onclick="javascript:addsong({$SONG.song_id});"><img src="/images/add.gif" border="0" /></a></h2>


            <table width="750" cellspacing="8">
              <tr>
                <td width="50%" colspan="2">
                {if $ARTIST_COVER ne ''}
                <img src="/browse/artist/cover/{$SONG.artist_id}/" border="0" />
                {/if}
                </td>
                <td width="50%" colspan="2">
                {if $ALBUM_COVER ne ''}
                <img src="/browse/albums/cover/{$SONG.album_id}/" border="0" />
                {/if}
                </td>
              </tr>
              <tr>
                <td width="20%">Artist:</td>
                <td width="30%"><a href="/browse/artists/byid/{$SONG.artist_id}/">{$SONG.name}</a></td>
                <td width="20%">Album:</td>
                <td width="30%"><a href="/browse/albums/byid/{$ALBUM.0.album_id}/">{$ALBUM.0.title}</a></td>
              </tr>
              <tr>
                <td width="20%">Genre:</td>
                <td width="30%">{$SONG.genre_id}</td>
                <td width="20%">Year:</td>
                <td width="30%">{$SONG.year}</td>
              </tr>
              <tr>
                <td width="20%">Bitrate:</td>
                <td width="30%">{$SONG.bitrate}</td>
                <td width="20%">Duration:</td>
                <td width="30%">{$SONG.duration}</td>
              </tr>
              <tr>
                <td width="20%">Added to DB:</td>
                <td width="30%">{$SONG.added|date_format:"%d.%m.%Y@%H:%M:%S"}</td>
                <td width="20%">Filesize:</td>
                <td width="30%">{$SONG.filesize|bytesToHumanReadable}</td>
              </tr>
              <tr>
                <td width="20%">Played:</td>
                <td width="30%">{$SONG.played}</td>
                <td width="20%">Skipped:</td>
                <td width="30%">{$SONG.skipped}</td>
              </tr>
              <tr>
                <td width="20%">Downloaded:</td>
                <td width="30%">{$SONG.downloaded}</td>
                <td width="20%">Voted:</td>
                <td width="30%">{$SONG.voted}</td>
              </tr>
              <tr>
                <td colspan="4"><a href="/download/song/{$SONG.song_id}/">Download this Song</a></td>
              </tr>
            </table>

<h3>Lyrics</h3>

{if $SONG.lyrics ne ''}
<p>{$SONG.lyrics|nl2br}</p>
{else}
<p>no lyrics available</p>
{/if}
