						<h1><a name="intro" id="intro"></a>Browse by artists</h1>

						{include file='artist/alpha_index.tpl'}


			<div id="alpha_results">
						{include file='artist/list_results.tpl'}
            </div>
				<form id="helperform" name="helperform">
				<input type="hidden" name="alpha" value="{$ALPHA}" />
				<input type="hidden" name="active_node" value="artist" />
				</form>
