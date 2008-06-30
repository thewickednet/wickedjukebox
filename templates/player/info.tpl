<table cellpadding="6" cellspacing="0" width="100%">
<tr>
<td width="30%"><img src="/img.php?category=song&preset=player&id={$PLAYER_STATUS.songinfo.id}" align="left" vspace="7" hspace="7" style="border: 1px solid #cccccc; background-color: #ffffff; padding: 3px; margin-right: 2px; margin-top: 3px;" /></td>
<td width="70%">
            {if count($PLAYER_STATUS) ne '0'}
<h2>{$PLAYER_STATUS.artistinfo.name}</h2>{$PLAYER_STATUS.songinfo.title}<br />({$PLAYER_STATUS.songinfo.duration|date_format:"%M:%S"})
            <script>
            document.title = '{$PLAYER_STATUS.artistinfo.name|escape:javascript} - {$PLAYER_STATUS.songinfo.title|escape:javascript}' + ' is currently playing @ Wicked Player';
            </script>
            {else}
            <p>Status: not available</p>
            <script>
            document.title = 'Wicked Player';
            </script>
            {/if}
</td>
</tr>
</table>
