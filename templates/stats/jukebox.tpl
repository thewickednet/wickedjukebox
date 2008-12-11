
						<h1><a name="intro" id="intro"></a>Statistics</h1>

            <h3>General</h3>

            	<table cellspacing="1" cellpadding="4" width="100%">
                  <tr class="resultlist">
            		<td align="right" width="5%">&nbsp;&nbsp;</td>
                    <td width="70%">Total Songs</td>
                    <td align="right" width="25%">{$SONG_TOTAL}</td>
                  </tr>
                  <tr class="resultlist">
            		<td align="right" width="5%">&nbsp;&nbsp;</td>
                    <td width="70%">Total Songs in diskspace</td>
                    <td align="right" width="25%">{$SONG_SIZE|bytesToHumanReadable}</td>
                  </tr>
                  <tr class="resultlist">
            		<td align="right" width="5%">&nbsp;&nbsp;</td>
                    <td width="70%">Total Albums</td>
                    <td align="right" width="25%">{$ALBUM_TOTAL}</td>
                  </tr>
                  <tr class="resultlist">
            		<td align="right" width="5%">&nbsp;&nbsp;</td>
                    <td width="70%">Total Artists</td>
                    <td align="right" width="25%">{$ARTIST_TOTAL}</td>
                  </tr>
                  <tr class="resultlist">
            		<td align="right" width="5%">&nbsp;&nbsp;</td>
                    <td width="70%">Total Users</td>
                    <td align="right" width="25%">{$USER_TOTAL}</td>
                  </tr>
                </table>

            <h3>Most Played Songs</h3>

            {if count($SONG_PLAYS) > 0}
            {counter name="items" print=false start=0}
            	<table cellspacing="1" cellpadding="4" width="100%">
            	{foreach from=$SONG_PLAYS item=ITEM}
                  <tr class="resultlist">
            		<td align="right" width="5%">{counter name="items" print=true}.&nbsp;&nbsp;</td>
                    <td width="45%"><a href="/song/detail/{$ITEM.song_id}/">{$ITEM.song_title}</a></td>
                    <td width="45%"><a href="/artists/detail/{$ITEM.artist_id}/">{$ITEM.artist_name}</a></td>
                    <td align="right" width="5%">{$ITEM.counter}</td>
                  </tr>
                {/foreach}
                </table>
            {else}
            <p>no songs have been queued yet</p>
            {/if}

            <h3>Most Played Albums</h3>

            {if count($ALBUM_PLAYS) > 0}
            {counter name="items" print=false start=0}
            	<table cellspacing="1" cellpadding="4" width="100%">
            	{foreach from=$ALBUM_PLAYS item=ITEM}
                  <tr class="resultlist">
            		<td align="right" width="5%">{counter name="items" print=true}.&nbsp;&nbsp;</td>
                    <td width="45%"><a href="/album/detail/{$ITEM.album_id}/">{$ITEM.album_name}</a></td>
                    <td width="45%"><a href="/artists/detail/{$ITEM.artist_id}/">{$ITEM.artist_name}</a></td>
                    <td align="right" width="5%">{$ITEM.counter}</td>
                  </tr>
                {/foreach}
                </table>
            {else}
            <p>no albums have been queued yet</p>
            {/if}
            
            <h3>Artists with most Songs</h3>

            {if count($ARTIST_SONGS) > 0}
            {counter name="items" print=false start=0}
            	<table cellspacing="1" cellpadding="4" width="100%">
            	{foreach from=$ARTIST_SONGS item=ITEM}
                  <tr class="resultlist">
            		<td align="right" width="5%">{counter name="items" print=true}.&nbsp;&nbsp;</td>
                    <td width="90%"><a href="/artists/detail/{$ITEM.artist_id}/">{$ITEM.artist_name}</a></td>
                    <td align="right" width="5%">{$ITEM.counter}</td>
                  </tr>
                {/foreach}
                </table>
            {else}
            <p>no songs found</p>
            {/if}

            <h3>Artists with most Albums</h3>

            {if count($ARTIST_ALBUMS) > 0}
            {counter name="items" print=false start=0}
            	<table cellspacing="1" cellpadding="4" width="100%">
            	{foreach from=$ARTIST_ALBUMS item=ITEM}
                  <tr class="resultlist">
            		<td align="right" width="5%">{counter name="items" print=true}.&nbsp;&nbsp;</td>
                    <td width="90%"><a href="/artists/detail/{$ITEM.artist_id}/">{$ITEM.artist_name}</a></td>
                    <td align="right" width="5%">{$ITEM.counter}</td>
                  </tr>
                {/foreach}
                </table>
            {else}
            <p>no albums found</p>
            {/if}
            
            
            <h3>Most Loved Songs</h3>

            {if count($SONGS_LOVE) > 0}
            {counter name="items" print=false start=0}
            	<table cellspacing="1" cellpadding="4" width="100%">
            	{foreach from=$SONGS_LOVE item=ITEM}
                  <tr class="resultlist">
            		<td align="right" width="5%">{counter name="items" print=true}.&nbsp;&nbsp;</td>
                    <td width="45%"><a href="/song/detail/{$ITEM.song_id}/">{$ITEM.song_title}</a></td>
                    <td width="45%"><a href="/artists/detail/{$ITEM.artist_id}/">{$ITEM.artist_name}</a></td>
                    <td align="right" width="5%">{$ITEM.counter}</td>
                  </tr>
                {/foreach}
                </table>
            {else}
            <p>no loved songs found</p>
            {/if}
            
            <h3>Most Hated Songs</h3>

            {if count($SONGS_HATE) > 0}
            {counter name="items" print=false start=0}
            	<table cellspacing="1" cellpadding="4" width="100%">
            	{foreach from=$SONGS_HATE item=ITEM}
                  <tr class="resultlist">
            		<td align="right" width="5%">{counter name="items" print=true}.&nbsp;&nbsp;</td>
                    <td width="45%"><a href="/song/detail/{$ITEM.song_id}/">{$ITEM.song_title}</a></td>
                    <td width="45%"><a href="/artists/detail/{$ITEM.artist_id}/">{$ITEM.artist_name}</a></td>
                    <td align="right" width="5%">{$ITEM.counter}</td>
                  </tr>
                {/foreach}
                </table>
            {else}
            <p>no hated songs found</p>
            {/if}
            
            <h3>Most Active users</h3>

            {if count($USER_ACTIVE) > 0}
            {counter name="items" print=false start=0}
            	<table cellspacing="1" cellpadding="4" width="100%">
            	{foreach from=$USER_ACTIVE item=ITEM}
                  <tr class="resultlist">
            		<td align="right" width="5%">{counter name="items" print=true}.&nbsp;&nbsp;</td>
                    <td width="70%"><a href="/?module=user&action=detail&id={$ITEM.id}">{$ITEM.fullname}</a></td>
                    <td align="right" width="25%">{$ITEM.selects} songs queued</td>
                  </tr>
                {/foreach}
                </table>
            {else}
            <p>no active users found</p>
            {/if}
            
            <h3>Loudest users</h3>

            {if count($USER_SHOUT) > 0}
            {counter name="items" print=false start=0}
            	<table cellspacing="1" cellpadding="4" width="100%">
            	{foreach from=$USER_SHOUT item=ITEM}
                  <tr class="resultlist">
            		<td align="right" width="5%">{counter name="items" print=true}.&nbsp;&nbsp;</td>
                    <td width="70%"><a href="/?module=user&action=detail&id={$ITEM.id}">{$ITEM.fullname}</a></td>
                    <td align="right" width="25%">{$ITEM.counter} shouts</td>
                  </tr>
                {/foreach}
                </table>
            {else}
            <p>no active users found</p>
            {/if}
            
