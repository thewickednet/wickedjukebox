            <h1><a name="intro" id="intro"></a>Favorites</h1>

            <h2>{$USER.fullname}</h2>

            <table cellspacing="6" width="700">
            <tr>
              <td><b>Total Favorites:</b> {$RESULT_COUNT}</td>
              <td rowspan="2" align="right">
                <img src="/img.php?category=user&preset=favorites&id={$USER.id}" style="border: 1px solid #cccccc; background-color: #ffffff; padding: 3px; margin-right: 2px; margin-top: 3px;" id="img_album"/>
              </td>
            </tr>
            <tr>
              <td><b>Total Hates:</b> {$USER.downloads}</td>
            </tr>
            </table>


                {if count($RESULTS) ne '0'}
            <div id="results">
                {include file='user/favorites_results.tpl'}
            </div>
                {else}
                <p>no favorites found. please use the love &amp; hate icons next to the NOW PLAYING track.</p>
                {/if}

<form id="helperform" name="helperform">
<input type="hidden" name="param" value="{$USER.id}" />
<input type="hidden" name="module" value="user" />
<input type="hidden" name="action" value="favorites" />
</form>

<form method="post">
<p>Want to discover some new music? Check out the favorites of other users:
<select onchange="location = this.options[this.selectedIndex].value;">
{foreach from=$USERS item=ITEM}
<option value="/user/favorites/{$ITEM.id}/" {if $ITEM.id eq $USER.id}selected{/if}>{$ITEM.fullname}</option>
{/foreach}
</select>
</p></form>
