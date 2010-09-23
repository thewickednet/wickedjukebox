
<h1><a name="intro" id="intro"></a>Event Details</h1>

<h2>{$EVENT.title}</h2>


            <table cellspacing="6" width="700">
            <tr>
              <td>Date:</b> {$EVENT.startdate|date_format:"%d.%m.%Y @ %H:%M"} - {$EVENT.enddate|date_format:"%d.%m.%Y @ %H:%M"}</td>
              <td rowspan="2" align="right" valign="top">
                <img src="/img.php?category=event&preset=detail&id={$EVENT.id}" style="border: 1px solid #cccccc; background-color: #ffffff; padding: 3px; margin-right: 2px; margin-top: 3px;" id="img_album"/>
              </td>
            </tr>
            <tr>
              <td>
{if $EVENT.lon ne '' && $EVENT.lat ne ''}
{$lon} / {$lat}
{/if}
              </td>
            </tr>
            </table>

            
            <h3>Most Played Songs at this Event</h3>

            {if $SONG_COUNT > 0}
            {counter name="items" print=false start=0}
            	<table cellspacing="1" cellpadding="4" width="100%">
            	{foreach from=$SONGS item=ITEM}
                  <tr class="resultlist">
            		<td align="right" width="5%">{counter name="items" print=true}.&nbsp;&nbsp;</td>
                    <td width="45%"><a href="/song/detail/{$ITEM.song_id}/">{$ITEM.song_title}</a></td>
                    <td width="45%"><a href="/artist/detail/{$ITEM.artist_id}/">{$ITEM.artist_name}</a></td>
                    <td align="right" width="5%">{$ITEM.played}</td>
                  </tr>
                {/foreach}
                </table>
            {else}
            <p>no songs have been queued yet</p>
            {/if}

            <h3>Most Active Users at this Event</h3>

            {if $USER_COUNT > 0}
            {counter name="items" print=false start=0}
            	<table cellspacing="1" cellpadding="4" width="100%">
            	{foreach from=$USERS item=ITEM}
                  <tr class="resultlist">
            		<td align="right" width="5%">{counter name="items" print=true}.&nbsp;&nbsp;</td>
                    <td width="70%"><a href="/?module=user&action=detail&id={$ITEM.id}">{$ITEM.fullname}</a></td>
                    <td align="right" width="25%">{$ITEM.songs} songs queued</td>
                  </tr>
                {/foreach}
                </table>
            {else}
            <p>no active users found</p>
            {/if}
