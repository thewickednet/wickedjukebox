
            <p>
            {foreach from=$ALPHA_INDEX key=KEY item=VALUE name=alist}
            {if $KEY ne $ALPHA}
                <a href="javascript:;" onclick="javascript:listAlpha('{$KEY}');">{$VALUE}</a>{if !$smarty.foreach.alist.last} -{/if}
            {else}
                {$VALUE}{if !$smarty.foreach.alist.last} -{/if}
            {/if}
            {/foreach}
            </p>
