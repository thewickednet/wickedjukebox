<h1><a name="intro" id="intro"></a>EVENTS</h1>


	<h2>Upcoming Events</h2>
            <table width="100%" cellpadding="0" cellspacing="8">
            {counter start=0 print=false assign=mycounter}
            {foreach from=$UPCOMING_EVENTS item=EVENT}
            {capture name="column"}{math equation="x % 2" x=$mycounter}{/capture}
            {if $smarty.capture.column == "0"}<tr>{/if}
                    <td width="90"><a href="/event/detail/{$EVENT.id}/"><img src="/img.php?category=event&preset=list&id={$EVENT.id}" style="border: 1px solid #cccccc; background-color: #ffffff; padding: 3px; margin-right: 2px; margin-top: 3px;" id="img_artist"/></a></td>
                    <td width="250"><a href="/event/detail/{$EVENT.id}/">{$EVENT.title}</a> <br />
                    {$EVENT.startdate|date_format:"%d.%m.%Y @ %H:%M"} - {$EVENT.enddate|date_format:"%d.%m.%Y @ %H:%M"}
                    </td>
            {if $smarty.capture.column == "1"}</tr>{/if}
            {counter print=false}
            {/foreach}
            {if $smarty.capture.column == "0"}<td></td></tr>{/if}
            </table>


	<h2>Past Events</h2>

            <table width="100%" cellpadding="0" cellspacing="8">
            {counter start=0 print=false assign=mycounter}
            {foreach from=$EVENTS_PAST item=EVENT}
            {capture name="column"}{math equation="x % 2" x=$mycounter}{/capture}
            {if $smarty.capture.column == "0"}<tr>{/if}
                    <td width="90"><a href="/event/detail/{$EVENT.id}/"><img src="/img.php?category=event&preset=list&id={$EVENT.id}" style="border: 1px solid #cccccc; background-color: #ffffff; padding: 3px; margin-right: 2px; margin-top: 3px;" id="img_artist"/></a></td>
                    <td width="250"><a href="/event/detail/{$EVENT.id}/">{$EVENT.title}</a><br />
                    {$EVENT.startdate|date_format:"%d.%m.%Y @ %H:%M"} - {$EVENT.enddate|date_format:"%d.%m.%Y @ %H:%M"}<br />
                    {$EVENT.songs} songs
                    </td>
            {if $smarty.capture.column == "1"}</tr>{/if}
            {counter print=false}
            {/foreach}
            {if $smarty.capture.column == "0"}<td></td></tr>{/if}
            </table>


