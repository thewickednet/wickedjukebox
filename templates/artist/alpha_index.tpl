
            <p>
            {foreach from=$ALPHA_INDEX key=KEY item=VALUE name=alist}
            {if $KEY ne $ALPHA}
                <a href="#" onclick="javascript:listAlpha('{$KEY}');">{$VALUE}</a>{if !$smarty.foreach.alist.last} -{/if}
            {else}
                {$VALUE}{if !$smarty.foreach.alist.last} -{/if}
            {/if}
            {/foreach}
            <br />
            <a href="/browse/artist/various/">Various</a> -
            <a href="/browse/artist/ost/">Soundtrack</a> -
            <a href="/browse/artist/videogame/">Video Games</a>
            </p>
