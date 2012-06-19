<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">

<!-- Web Page Design by James Koster - http://www.jameskoster.co.uk -->

<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Wicked Jukebox 2.o</title>
<link href="/style.css" rel="stylesheet" type="text/css" />
<link href="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8/themes/base/jquery-ui.css" rel="stylesheet" type="text/css"/>
<link rel="shortcut icon" href="http://wickedjukebox.com/favicon.png" type="image/x-icon">
<link rel="icon" href="http://wickedjukebox.com/favicon.png" type="image/x-icon"> {literal}
  <script type="text/javascript" src="/javascript/jukebox.js"></script>
  <script type="text/javascript" src="/javascript/md5.js"></script>
  <script type="text/javascript" src="/javascript/overlib.js"></script>
<script src="https://www.google.com/jsapi?key=ABQIAAAAmJWIty3l04f-hP9etJ5tJxTtZ4N5dXLGUlJvVEwYk4QNCXmwgRSODbsU23oUdM0re3Cc5d6l-lQfKg" type="text/javascript"></script>
<script>
    google.load("jquery", "1.6.1");
    google.load("jqueryui", "1.8.13");
</script>
  <script type="text/javascript" src="/javascript/jquery.ba-dotimeout.min.js"></script>
  <script type="text/javascript" src="/javascript/jquery.innerfade.js"></script>
  <script type="text/javascript" src="/javascript/jquery.watermark.js"></script>
{/literal}
</head>

{if $CORE->active_node eq 'splash' && $CORE->user_id ne '-1'}
<body onload="javascript:autoRefreshSplash();">
{else}
<body onload="javascript:refreshQueuePeriodical('sidebar');">
{/if}

<div id="overDiv" style="position:absolute; visibility:hidden; z-index:1000;"></div>
<div id="hiddenDiv" style="position:absolute; visibility:hidden; z-index:1000"></div>
<div id="container">
<a name="top" id="top"></a>
<center>
		<div id="menu">
                {if $PLAYER_STATUS.auth eq 'yes'}
				<a href="/" {if $CORE->active_node eq 'splash'}class="active"{/if}>splash</a> <a href="/artist/browse/" {if $CORE->active_node eq 'artist'}class="active"{/if}>artists</a> <a href="/album/browse/" {if $CORE->active_node eq 'album'}class="active"{/if}>albums</a> <a href="/user/favorites/" {if $CORE->active_node eq 'favorites'}class="active"{/if}>favorites</a> <a href="/event/" {if $CORE->active_node eq 'event'}class="active"{/if}>events</a> <a href="/song/history/" {if $CORE->active_node eq 'history'}class="active"{/if}>history</a> <a href="/album/latest/" {if $CORE->active_node eq 'latest'}class="active"{/if}>latest additions</a> <a href="/stats/" {if $CORE->active_node eq 'stats'}class="active"{/if}>statistics</a>{if $CORE->permissions.admin eq '1'} <a href="/admin/" {if $CORE->active_node eq 'admin'}class="active"{/if}>admin</a>{/if} <a href="/auth/logout/">logout</a>
				{/if}
        </div>

		<div id="header">
<div id="search">
		  {if $PLAYER_STATUS.auth eq 'yes'}
			<form name="searchform" action="/search/" class="search" method="post">
		    <img src="/images/carousel.gif" align="left" style="display:none;" id="search_carousel" />&nbsp;&nbsp;
		   <input id="search_input" type="text" name="pattern" maxlength="20" value="{$SEARCH_PATTERN}" />
			<select name="mode">
            <option value="any">Any</option>
            <option value="artist">Artist</option>
            <option value="album">Album</option>
            <option value="song">Song</option>
            {*<option value="lyrics">Lyrics</option>*}
          </select>
					{*<input type="submit" value="Find!"  />*}
          </form>
<div id="search_preview">
</div>
</div>
          {/if}
				<h1><a href="/"><img border="0" src="/images/jukebox_logo.jpg" /></a></h1>
		</div>

		<div id="content">
          <img src="/images/carousel.gif" width="0" height="0" />
          <img src="/images/tick.png" width="0" height="0" />
          <img src="/images/exclamation.png" width="0" height="0" />
          {if $CORE->permissions.queue_skip eq '1'}
          <a href="javascript:;" onclick="javascript:control('next');" id="control_next">&nbsp;&nbsp;&nbsp;&nbsp;</a>
          {/if}

{if $CORE->active_node eq 'splash' && $CORE->user_id ne '-1'}
    <div id="splash">
	      {include file='splash/splash.tpl'}
	</div>
{elseif $CORE->active_node eq 'search' && $CORE->user_id ne '-1'}
    <div id="search_results_list">
	      {include file='search.tpl'}
	</div>
{else}

				<div id="sidebar">
		  <div id="controls">
          {if $CORE->user_id ne '-1'}
		  {*
          <a href="#" onclick="javascript:control('stop');" id="control_stop">&nbsp;</a>
          <a href="#" onclick="javascript:control('pause');" id="control_pause">&nbsp;</a>
          <a href="#" onclick="javascript:control('play');" id="control_play">&nbsp;</a>
          *}
          {/if}
          </div>
          
          <div id="login">
          {if $CORE->user_id eq '-1'}
          {include file='login.tpl'}
          {else}
          {include file='profile.tpl'}
          {/if}
          </div>
                    {if $PLAYER_STATUS.auth eq 'yes'}
					<div class="submenu" id="queue">
					{include file='queue.tpl'}
					</div>

					<div class="submenu" id="shoutbox">
					{include file='shoutbox/box.tpl'}
					</div>

					<div class="submenu" id="random">
					{include file='song/random.tpl'}
					</div>
					{/if}

				</div>

				<div id="mainbar">
				<div id="helper">
				
				</div>
				<div id="body">
		  {if $BODY_TEMPLATE ne ''}
	      {include file=$BODY_TEMPLATE}
	      {/if}
	      </div>
		  </div>
 {/if}
  </div>
  <div style="height: 50px; clear:both;">&nbsp;</div>
  <div id="footer">
 		wicked jukebox 2.o<br />
  Design based on <a href="http://www.oswd.org/design/preview/id/2087" target="_blank">Plain 1.0</a> by <a href="http://www.jameskoster.co.uk" target="_blank">James Koster</a> - Logo by <a href="http://www.koreatabs.de" target="_blank">Jens Lumm</a> - all the rest by exhuma.twn & doc.twn - <a href="http://www.wicked.lu" target="_blank">The Wicked Net</a></div>
 </center>

{if $CORE->active_node ne 'search'}
{literal}
<script>
$('#search_input').watermark('Search!', {className: 'watermark'});
</script>
{/literal}
{/if}
{*
{literal}
<script>
$(document).ready(function(){
$("#search_input").keyup(function() 
{
var searchbox = $(this).val();
var dataString = 'pattern='+ searchbox;
if(searchbox=='')
{}
else
{
$.ajax({
type: "POST",
url: "/search/preview/",
data: dataString,
cache: false,
success: function(html)
{
$("#search_preview").html(html).show();
}
});
}return false; 
});
});
</script>
{/literal}
*}
</div>
</body>
</html>
