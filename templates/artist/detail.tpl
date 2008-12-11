
            <h1><a name="intro" id="intro"></a>Artist Details</h1>

            <h2>{$ARTIST.name}
            {if $ARTIST.name ne 'Various Artists' && $ARTIST.name ne 'Soundtracks' && $ARTIST.name ne 'Video Games'}
            <div style="float: right"><a href="javascript:;" onclick="javascript:setArtistStanding({$ARTIST.id}, 'love');"><img src="/images/emoticon_happy.png" title="love this artist!" border="0" class="icon"/></a>&nbsp;<a href="javascript:;" onclick="javascript:setArtistStanding({$ARTIST.id}, 'neutral');"><img src="/images/emoticon_smile.png" title="this artist is ok!" border="0" class="icon"/></a>&nbsp;<a href="javascript:;" onclick="javascript:setArtistStanding({$ARTIST.id}, 'hate');"><img src="/images/emoticon_unhappy.png" title="hate this artist!" border="0" class="icon"/></a></div>
            {/if}
            </h2>

            {if $ARTIST.name eq 'Various Artists' || $ARTIST.name eq 'Soundtracks' || $ARTIST.name eq 'Video Games'}
            <h3>Songs in this category</h3>
            {else}
                <img src="/img.php?category=artist&preset=detail&id={$ARTIST.id}" style="border: 1px solid #cccccc; background-color: #ffffff; padding: 3px; margin-right: 2px; margin-top: 3px;" id="img_artist"/>
            <h3>Songs by this artist ({$RESULT_COUNT} entries)</h3>
	    {/if}
            <div id="results">
            {include file='artist/detail_results.tpl'}
            </div>
				<form id="helperform" name="helperform">
				<input type="hidden" name="param" value="{$ARTIST.id}" />
				<input type="hidden" name="module" value="artist" />
				</form>
