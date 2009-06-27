						<h1><a name="intro" id="intro"></a>Song Details</h1>

            <h2>
            {$SONG.title}{if $CORE->permissions.queue_add eq '1'}&nbsp;&nbsp;<a href="javascript:;" onclick="javascript:addsong({$SONG.id});"><img src="/images/add.png" title="queue this track" class="button" /></a>{/if}
            <div style="float: right"><a href="javascript:;" onclick="javascript:setStanding({$SONG.id}, 'love', 'detail');"><img src="/images/emoticon_happy.png" title="love this track!" border="0" class="icon{if $STANDING == 'love'}a{/if}"/></a>&nbsp;<a href="javascript:;" onclick="javascript:setStanding({$SONG.id}, 'neutral', 'detail');"><img src="/images/emoticon_smile.png" title="this track is ok!" border="0" class="icon{if $STANDING != 'love' && $STANDING != 'hate'}a{/if}"/></a>&nbsp;<a href="javascript:;" onclick="javascript:setStanding({$SONG.id}, 'hate', 'detail');"><img src="/images/emoticon_unhappy.png" title="hate this track!" border="0" class="icon{if $STANDING == 'hate'}a{/if}"/></a>&nbsp;<a href="javascript:;" onclick="javascript:setStanding({$PLAYER_STATUS.songinfo.id}, 'broken');"><img src="/images/error.png" title="report track as broken or very bad quality" border="0" class="icon" /></a></div>
            </h2>

            <table width="750" cellspacing="8">
              <tr>
                <td width="50%" colspan="2">
                <a href="/artist/detail/{$ARTIST.id}/"><img src="/img.php?category=artist&preset=detail&id={$ARTIST.id}" style="border: 1px solid #cccccc; background-color: #ffffff; padding: 3px; margin-right: 2px; margin-top: 3px;" id="img_artist"/></a>
                </td>
                <td width="50%" colspan="2">
                {if $ALBUM.name ne ''}
                <a href="/album/detail/{$ALBUM.id}/"><img src="/img.php?category=album&preset=detail&id={$ALBUM.id}" style="border: 1px solid #cccccc; background-color: #ffffff; padding: 3px; margin-right: 2px; margin-top: 3px;" id="img_album"/></a>
                {/if}
                </td>
              </tr>
              <tr>
                <td width="20%"><b>Artist:</b></td>
                <td width="30%"><a href="/artist/detail/{$ARTIST.id}/">{$ARTIST.name}</a></td>
                {if $ALBUM.name ne ''}
                <td width="20%"><b>Album:</b></td>
                <td width="30%"><a href="/album/detail/{$ALBUM.id}/">{$ALBUM.name}</a></td>
                {else}
                <td colspan="2">&nbsp;</td>
                {/if}
              </tr>
              <tr>
                <td width="20%"><b>Genre:</b></td>
                <td width="30%">
                {foreach from=$GENRES item=GENRE}
                {$GENRE.name}
                {/foreach}
                </td>
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
                <td width="30%">{$CHANNEL_DATA.lastPlayed|date_format:"%d.%m.%Y@%H:%M:%S"}</td>
                <td width="20%">&nbsp;</td>
                <td width="30%">&nbsp;</td>
              </tr>
              <tr>
                <td width="20%"><b>Played:</b></td>
                <td width="30%">{$CHANNEL_DATA.played}</td>
                <td width="20%"><b>Skipped:</b></td>
                <td width="30%">{$CHANNEL_DATA.skipped}</td>
              </tr>
              <tr>
                <td width="20%"><b>Downloaded:</b></td>
                <td width="30%">{$SONG.downloaded}</td>
                <td width="20%"><b>Voted:</b></td>
                <td width="30%">{$SONG.voted}</td>
              </tr>
              {if $CORE->permissions.admin eq '1'}
              <tr>
                <td colspan="4"><b>Filename:</b> {$SONG.localpath}</td>
              </tr>
              {/if}
              <tr>
                <td width="20%"><b>Loved:</b></td>
                <td width="30%">
                {if $LOVES_COUNT > 0}
                    <a href="javascript:void(0);" onmouseover="return overlib('User who love this song:<br>{foreach from=$LOVES item=LOVE_ITEM}{$LOVE_ITEM.fullname}<br>{/foreach}');" onmouseout="return nd();">{$LOVES_COUNT}</a>
                {else}
                    {$LOVES_COUNT}
                {/if}
                </td>
                <td width="20%"><b>Hated:</b></td>
                <td width="30%">
                {if $HATES_COUNT > 0}
                    <a href="javascript:void(0);" onmouseover="return overlib('User who hate this song:<br>{foreach from=$HATES item=HATE_ITEM}{$HATE_ITEM.fullname}<br>{/foreach}');" onmouseout="return nd();">{$HATES_COUNT}</a>
                {else}
                    {$HATES_COUNT}
                {/if}
                </td>
              </tr>
              <tr>
                <td colspan="4"><a href="/song/download/{$SONG.id}/">Download this Song</a></td>
              </tr>
            </table>

<h3>Lyrics</h3>


<p><a href="javascript:;" onclick="javascript:getLyrics({$SONG.id});">Update Lyrics</a> <img src="/images/carousel.gif" style="display:none;" id="lyrics_carousel" /> {if $LYRICS_ERROR ne ''}<strong>{$LYRICS_ERROR}</strong>{/if}</p>


{if $SONG.lyrics ne ''}
<p>{$SONG.lyrics|nl2br}</p>
{else}

<p>no lyrics available</p>
{/if}
