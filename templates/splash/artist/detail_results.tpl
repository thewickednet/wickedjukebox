            <p align="center">{$LINKS}</p>
            {foreach from=$ALBUMS item=ALBUM}
            <h3>{if $CORE->permissions.queue_add eq '1'} <a href="javascript:;" onclick="javascript:addalbum({$ALBUM.id});"><img src="/images/add.png" title="queue the entire album" class="button" /></a> {if $ALBUM.love.count ne '0'}<a href="javascript:;" onclick="javascript:queueAlbumFavourites({$ALBUM.id});"><img src="/images/heart.png" title="Queue all my favourites from this album" border="0" /></a>{/if}{/if} {$ALBUM.name} {if $ALBUM.release_date ne '0000-00-00' && $ALBUM.release_date ne ''}({$ALBUM.release_date|date_format:"%Y"}){/if}
			<div style="float: right"><a href="javascript:;" onclick="javascript:setAlbumStanding({$ALBUM.id}, 'love');"><img src="/images/emoticon_happy.png" title="love this album!" border="0" class="icon"/></a>&nbsp;<a href="javascript:;" onclick="javascript:setAlbumStanding({$ALBUM.id}, 'neutral');"><img src="/images/emoticon_smile.png" title="this album is ok!" border="0" class="icon"/></a>&nbsp;<a href="javascript:;" onclick="javascript:setAlbumStanding({$ALBUM.id}, 'hate');"><img src="/images/emoticon_unhappy.png" title="hate this album!" border="0" class="icon"/></a></div>
			</h3>
            <table class="albums">
			<tr>
			<td width="130" valign="top">
			<a href="/album/detail/{$ALBUM.id}/"><img src="/img.php?category=album&preset=list&id={$ALBUM.id}" style="border: 1px solid #cccccc; background-color: #ffffff; padding: 3px; margin-right: 2px; margin-top: 3px;" alt="{$ALBUM.name}" title="{$ALBUM.name}" id="img_artist"/></a>
			</td>
			<td width="570">
			<table class="songs">
			{foreach from=$ALBUM.songs item=SONG}
              <tr {if $SONG.standing ne ''}class="{$SONG.standing}"{/if}>
                <td>{if $CORE->permissions.queue_add eq '1'}<a href="javascript:;" onclick="javascript:addsong({$SONG.id});"><img src="/images/bullet_add.png" class="button" /></a>{/if}</td>
                <td><a href="/song/detail/{$SONG.id}/">{$SONG.title}</a></td>
                <td align="right">{$SONG.duration|date_format:"%M:%S"} ({$SONG.cost} <img src="/images/money.png" class="button" />)</td>
                <td align="right"><img src="/popgraph.php?value={$SONG.prating}" title="{$SONG.num_loves[0].counter|default:'0'} loves, {$SONG.num_hates[0].counter|default:'0'} hates" /></td>
              </tr>
              {/foreach}
			</table>
			</td>
            </table>

            {/foreach}
            <p align="center">{$LINKS}</p>
