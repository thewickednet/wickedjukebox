						<h1><a name="intro" id="intro"></a>Browse by albums</h1>

						{include file='album/alpha_index.tpl'}

            <div id="alpha_results">
						{include file='album/list_results.tpl'}
            </div>
           	<form id="helperform" name="helperform">
				<input type="hidden" name="alpha" value="{$ALPHA}" />
				<input type="hidden" name="active_node" value="album" />
			</form>
