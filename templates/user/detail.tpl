						<h1><a name="intro" id="intro"></a>User Details</h1>

            <h2>{$USER.fullname}</h2>

            <table cellspacing="6" width="700">
            <tr>
              <td><b>Group:</b> {$GROUP.title}</td>
              <td rowspan="5" align="right">
                <img src="/img.php?category=user&preset=profile&id={$USER.id}" style="border: 1px solid #cccccc; background-color: #ffffff; padding: 3px; margin-right: 2px; margin-top: 3px;" id="img_album"/>
              </td>
            </tr>
            <tr>
              <td><b>Songs Queued:</b> {$USER.selects}</td>
            </tr>
            <tr>
              <td><b>Downloads:</b> {$USER.downloads}</td>
            </tr>
            <tr>
              <td><b>Joined:</b> {$USER.added|date_format:"%d.%m.%Y@%H:%M:%S"}</td>
            </tr>
            <tr>
              <td><b>Last online:</b> {if $USER.proof_of_life eq '0000-00-00 00:00:00'}Never{else}{$USER.proof_of_life|date_format:"%d.%m.%Y@%H:%M:%S"}{/if}</td>
            </tr>
            </table>

<p>&nbsp;</p>
            <h3>{$USER.fullname} loves the following tracks (random 20 track pick, reload for more)</h3>
                {if count($LOVE) ne '0'}
                <table cellspacing="1" cellpadding="4" width="100%">
                {foreach from=$LOVE item=RESULT}
                  <tr class="resultlist">
                    <td><a href="/artist/detail/{$RESULT.artist_id}/">{$RESULT.artist_name}</a></td>
                    <td><a href="javascript:;" onclick="javascript:addsong({$RESULT.song_id});"><img src="/images/bullet_add.png" class="button" /></a> <a href="/song/detail/{$RESULT.song_id}/">{$RESULT.song_title}</a></td>
                    <td><a href="javascript:;" onclick="javascript:addalbum({$RESULT.album_id});"><img src="/images/bullet_add.png" class="button" /></a> <a href="/album/detail/{$RESULT.album_id}/">{$RESULT.album_name}</a></td>
                  </tr>
                {/foreach}
                </table>
                <p><a href="/user/favorites/{$USER.id}/">more...</a></p>
                {else}
                <p>this user doesn't have any favorite tracks.</p>
                {/if}

                
<p>&nbsp;</p>
            <h3>{$USER.fullname} hates the following tracks (random 20 track pick, reload for more)</h3>
                {if count($HATE) ne '0'}
                <table cellspacing="1" cellpadding="4" width="100%">
                {foreach from=$HATE item=RESULT}
                  <tr class="resultlist">
                    <td><a href="/artist/detail/{$RESULT.artist_id}/">{$RESULT.artist_name}</a></td>
                    <td><a href="javascript:;" onclick="javascript:addsong({$RESULT.song_id});"><img src="/images/bullet_add.png" class="button" /></a> <a href="/song/detail/{$RESULT.song_id}/">{$RESULT.song_title}</a></td>
                    <td><a href="javascript:;" onclick="javascript:addalbum({$RESULT.album_id});"><img src="/images/bullet_add.png" class="button" /></a> <a href="/album/detail/{$RESULT.album_id}/">{$RESULT.album_name}</a></td>
                  </tr>
                {/foreach}
                </table>
                {else}
                <p>this user doesn't hate any tracks.</p>
                {/if}

