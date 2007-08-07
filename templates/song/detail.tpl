						<h1><a name="intro" id="intro"></a>Song Details</h1>

            <h2>{$SONG.title}{if $CORE->permissions.queue_add eq '1'}&nbsp;&nbsp;<a href="#" onclick="javascript:addsong({$SONG.id});"><img src="/images/bullet_add.png" class="button" /></a>{/if}</h2>


            <table width="750" cellspacing="8">
              <tr>
                <td width="50%" colspan="2">
                {if $ARTIST_COVER ne ''}
                <img src="/cover/artist/{$SONG.artist_id}/" border="0" id="img_artist"/>
                {/if}
                </td>
                <td width="50%" colspan="2">
                {if $ALBUM_COVER ne ''}
                <img src="/cover/album/{$SONG.album_id}/" border="0" id="img_album"/>
                {/if}
                </td>
              </tr>
              <tr>
                <td width="20%"><b>Artist:</b></td>
                <td width="30%"><a href="/details/artist/{$ARTIST.id}/">{$ARTIST.name}</a></td>
                <td width="20%"><b>Album:</b></td>
                <td width="30%"><a href="/details/album/{$ALBUM.id}/">{$ALBUM.name}</a></td>
              </tr>
              <tr>
                <td width="20%"><b>Genre:</b></td>
                <td width="30%">{$SONG.genre_id}</td>
                <td width="20%"><b>Year:</b></td>
                <td width="30%">{$SONG.year}</td>
              </tr>
              <tr>
                <td width="20%"><b>Bitrate:</b></td>
                <td width="30%">{$SONG.bitrate}</td>
                <td width="20%"><b>Duration:</b></td>
                <td width="30%">{$SONG.duration|date_format:"%M:%S"}</td>
              </tr>
              <tr>
                <td width="20%"><b>Added to DB:</b></td>
                <td width="30%">{$SONG.added|date_format:"%d.%m.%Y@%H:%M:%S"}</td>
                <td width="20%"><b>Filesize:</b></td>
                <td width="30%">{$SONG.filesize|bytesToHumanReadable}</td>
              </tr>
              <tr>
                <td width="20%"><b>Last Played:</b></td>
                <td width="30%">{$SONG.lastplayed|date_format:"%d.%m.%Y@%H:%M:%S"}</td>
                <td width="20%">&nbsp;</td>
                <td width="30%">&nbsp;</td>
              </tr>
              <tr>
                <td width="20%"><b>Played:</b></td>
                <td width="30%">{$SONG.played}</td>
                <td width="20%"><b>Skipped:</b></td>
                <td width="30%">{$SONG.skipped}</td>
              </tr>
              <tr>
                <td width="20%"><b>Downloaded:</b></td>
                <td width="30%">{$SONG.downloaded}</td>
                <td width="20%"><b>Voted:</b></td>
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