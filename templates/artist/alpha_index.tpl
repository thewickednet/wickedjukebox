
            <p>
            {foreach from=$ALPHA_INDEX key=KEY item=VALUE name=alist}
            {if $KEY ne $ALPHA}
                <a href="javascript:;" onclick="javascript:listAlpha('{$KEY}');">{$VALUE}</a>{if !$smarty.foreach.alist.last} -{/if}
            {else}
                {$VALUE}{if !$smarty.foreach.alist.last} -{/if}
            {/if}
            {/foreach}
            <br />
            <a href="javascript:;" onclick="javascript:listSpecial('various');">Various</a> -
            <a href="javascript:;" onclick="javascript:listSpecial('ost');">Soundtrack</a> -
            <a href="javascript:;" onclick="javascript:listSpecial('game');">Video Games</a>
            </p>
