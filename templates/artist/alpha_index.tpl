
            <p>
            {foreach from=$ALPHA_INDEX key=KEY item=VALUE name=alist}
            {if $KEY ne $ALPHA}
                <a href="/artist/browse/{$KEY}/">{$VALUE}</a>{if !$smarty.foreach.alist.last} -{/if}
            {else}
                {$VALUE}{if !$smarty.foreach.alist.last} -{/if}
            {/if}
            {/foreach}
            <br />
            <a href="/album/browse/various/">Various</a> -
            <a href="/album/browse/ost/">Soundtrack</a> -
            <a href="/album/browse/game/">Video Games</a>
            </p>
