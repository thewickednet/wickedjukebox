
						<h1><a name="intro" id="intro"></a>100 Past Songs</h1>

            <div id="results">

                {if count($RESULTS) ne '0'}
                <table cellspacing="1" cellpadding="4">
                {foreach from=$RESULTS item=RESULT}
                  <tr class="resultlist">
                    <td><a href="javascript:;" onclick="javascript:addsong({$RESULT.song_id});"><img src="/images/bullet_add.png" class="button" /></a> <a href="/song/detail/{$RESULT.song_id}/">{$RESULT.track}</a></td>
                    <td align="right" nowrap>{$RESULT.time|date_format:"%d.%m.%Y@%H:%M:%S"}</td>
                  </tr>
                {/foreach}
                </table>
                {else}
                <p>no songs found</p>
                {/if}
            
            
            </div>
