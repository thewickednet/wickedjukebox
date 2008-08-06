            <p align="center">{$LINKS}</p>
            <table width="700" cellpadding="0" cellspacing="8">
            {counter start=0 print=false assign=mycounter}
            {foreach from=$ARTISTS item=ARTIST}
            {capture name="column"}{math equation="x % 2" x=$mycounter}{/capture}
            {if $smarty.capture.column == "0"}<tr>{/if}
                    <td width="90"><a href="/artist/detail/{$ARTIST.id}/"><img src="/img.php?category=artist&preset=list&id={$ARTIST.id}" style="border: 1px solid #cccccc; background-color: #ffffff; padding: 3px; margin-right: 2px; margin-top: 3px;" id="img_artist"/></a></td>
                    <td width="250"><a href="/artist/detail/{$ARTIST.id|lower}/">{$ARTIST.name}</a><br />{$ARTIST.songs} song{if $ARTIST.songs ne '1'}s{/if}</td>
            {if $smarty.capture.column == "1"}</tr>{/if}
            {counter print=false}
            {/foreach}
            {if $smarty.capture.column == "0"}<td></td></tr>{/if}
            </table>
            <p align="center">{$LINKS}</p>
