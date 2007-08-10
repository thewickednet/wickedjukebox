            <p align="center">{$LINKS}</p>
            <table width="100%" cellpadding="0" cellspacing="8">
            {counter start=0 print=false assign=mycounter}
            {foreach from=$ALBUMS item=ALBUM}
            {capture name="column"}{math equation="x % 2" x=$mycounter}{/capture}
            {if $smarty.capture.column == "0"}<tr>{/if}
                    <td width="50%"><a href="/details/album/{$ALBUM.album_id}/">{$ALBUM.album_name}</a><br />{$ALBUM.songs} song{if $ALBUM.songs ne '1'}s{/if}</td>
            {if $smarty.capture.column == "1"}</tr>{/if}
            {counter print=false}
            {/foreach}
            {if $smarty.capture.column == "0"}<td></td></tr>{/if}
            </table>
