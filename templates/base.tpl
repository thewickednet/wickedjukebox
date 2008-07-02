<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">

<!-- Web Page Design by James Koster - http://www.jameskoster.co.uk -->

<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Wicked Jukebox 2.o</title>
<link href="/style.css" rel="stylesheet" type="text/css" />
<link rel="shortcut icon" href="http://jukebox.wicked.lu/favicon.png" type="image/x-icon">
<link rel="icon" href="http://jukebox.wicked.lu/favicon.png" type="image/x-icon"> {literal}
  <script type="text/javascript" src="/javascript/prototype.js"></script>
  <script type="text/javascript" src="/javascript/jukebox.js"></script>
  <script type="text/javascript" src="/javascript/md5.js"></script>
  <script type="text/javascript" src="/javascript/scriptaculous/scriptaculous.js"></script>
{/literal}
</head>

<body onload="javascript:refreshQueuePeriodical();">
<div id="hiddenDiv" style="position:absolute; visibility:hidden; z-index:1000"></div>
<div id="container">
<a name="top" id="top"></a>
<center>
		<div id="menu">
                {if $PLAYER_STATUS.auth eq 'yes'}
				<a href="/browse/artist/" {if $CORE->active_node eq 'artist'}class="active"{/if}>artists</a> <a href="/browse/album/" {if $CORE->active_node eq 'album'}class="active"{/if}>albums</a> <a href="/browse/genres/">genres</a> {if $CORE->user_id ne '-1'}<a href="/?module=user&action=favorites" {if $CORE->active_node eq 'favorites'}class="active"{/if}>favorites</a> {/if}<a href="/?module=song&action=latest" {if $CORE->active_node eq 'latest'}class="active"{/if}>latest additions</a> <a href="/stats/" {if $CORE->active_node eq 'stats'}class="active"{/if}>statistics</a>{if $CORE->permissions.admin eq '1'} <a href="/?module=admin" {if $CORE->active_node eq 'admin'}class="active"{/if}>admin</a>{/if}
				{/if}
        </div>

		<div id="header">

		  {if $PLAYER_STATUS.auth eq 'yes'}
			<form name="searchform" onsubmit="return search();" class="search">
		    <img src="/images/carousel.gif" align="left" style="display:none;" id="search_carousel" />&nbsp;&nbsp;
		   <input type="text" name="pattern" maxlength="20" />
			<select name="mode">
            <option value="any">Any</option>
            <option value="artist">Artist</option>
            <option value="album">Album</option>
            <option value="song">Song</option>
            {*<option value="lyrics">Lyrics</option>*}
          </select>
					<input type="submit" value="Find!"  />
          </form>
          {/if}
				<h1>wicked jukebox 2.o</h1>
				<h2>hei spillt d'mus&eacute;k</h2>
		</div>

		<div id="content">
          <img src="/images/carousel.gif" width="0" height="0" />
          <img src="/images/tick.png" width="0" height="0" />
          <img src="/images/exclamation.png" width="0" height="0" />
<!--
				<img src="images/logo.jpg" alt="Your Logo" class="logo" />

				<p class="introduction">
						Hello and welcome to Plain version 1.0. This is a simple web site template maximising the use of css and xhtml. Whitespace is used in abundance to really push its importance in web design. Navigate the page via the menu at the top of the page, or the links underneath this paragraph.
				</p>
-->

				<div id="sidebar">
		  <div id="controls">
          {if $CORE->user_id ne '-1'}
				{*
          <a href="#" onclick="javascript:control('stop');" id="control_stop">&nbsp;</a>
          <a href="#" onclick="javascript:control('pause');" id="control_pause">&nbsp;</a>
          <a href="#" onclick="javascript:control('play');" id="control_play">&nbsp;</a>
          {if $CORE->permissions.queue_skip eq '1'}
          <a href="#" onclick="javascript:control('next');" id="control_next">&nbsp;</a>
          {/if}
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

  </div>
  <div style="height: 50px; clear:both;">&nbsp;</div>
  <div id="footer">
 		wicked jukebox 2.o<br />
  Design based on <a href="http://www.oswd.org/design/preview/id/2087" target="_blank">Plain 1.0</a> by <a href="http://www.jameskoster.co.uk">James Koster</a> - all the rest by exhuma.twn & doc.twn - <a href="http://www.wicked.lu" target="_blank">The Wicked Net</a></div>
 </center>

</div>

</body>
</html>
