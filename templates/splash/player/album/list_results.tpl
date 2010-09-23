            <p align="center">{$LINKS}</p>
            <table width="100%" cellpadding="0" cellspacing="8">
            {counter start=0 print=false assign=mycounter}
            {foreach from=$ALBUMS item=ALBUM}
            {capture name="column"}{math equation="x % 2" x=$mycounter}{/capture}
            {if $smarty.capture.column == "0"}<tr>{/if}
                    <td width="90"><a href="/album/detail/{$ALBUM.album_id}/"><img src="/img.php?category=album&preset=list&id={$ALBUM.album_id}" style="border: 1px solid #cccccc; background-color: #ffffff; padding: 3px; margin-right: 2px; margin-top: 3px;" id="img_artist"/></a></td>
                    <td width="250"><a href="/album/detail/{$ALBUM.album_id}/">{$ALBUM.album_name}</a>
                    {if $ALBUM.type eq 'album'}
                    <br />by <a href="/artist/detail/{$ALBUM.artist_id}/">{$ALBUM.artist_name}</a>
                    {/if}
                    <br />{$ALBUM.songs} song{if $ALBUM.songs ne '1'}s{/if}</td>
            {if $smarty.capture.column == "1"}</tr>{/if}
            {counter print=false}
            {/foreach}
            {if $smarty.capture.column == "0"}<td></td></tr>{/if}
            </table>
            <p align="center">{$LINKS}</p>
