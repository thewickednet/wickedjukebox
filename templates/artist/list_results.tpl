            <p align="center">{$LINKS}</p>
            <table width="100%">
            {counter start=0 print=false assign=mycounter}
            {foreach from=$ARTISTS item=ARTIST}
            {capture name="column"}{math equation="x % 2" x=$mycounter}{/capture}
            {if $smarty.capture.column == "0"}<tr>{/if}
                    <td width="50%"><a href="/details/artist/{$ARTIST.id|lower}/">{$ARTIST.name}</a></td>
            {if $smarty.capture.column == "1"}</tr>{/if}
            {counter print=false}
            {/foreach}
            {if $smarty.capture.column == "0"}<td></td></tr>{/if}
            </table>
