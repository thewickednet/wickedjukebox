<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">

<!-- Web Page Design by James Koster - http://www.jameskoster.co.uk -->

<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Wicked Jukebox 2.o</title>
<link href="/style.css" rel="stylesheet" type="text/css" />
{literal}
  <script type="text/javascript" src="/javascript/prototype.js"></script>
  <script type="text/javascript" src="/javascript/jukebox.js"></script>
  <script type="text/javascript" src="/javascript/md5.js"></script>
{/literal}
</head>

<body>
<div id="hiddenDiv" style="position:absolute; visibility:hidden; z-index:1000"></div>
<div id="container">
<a name="top" id="top"></a>
<center>
		<div id="menu">
				<a href="/browse/artist/">artists</a> <a href="/browse/album/">albums</a> <a href="/browse/genres/">genres</a> {if count($USERINFO) ne '0'}<a href="/browse/favorites/">favorites</a> {/if}<a href="/browse/latest/">latest additions</a> <a href="/stats/">statistics</a>{if $PERMISSIONS.admin eq '1'} <a href="/?section=admin">admin</a>{/if}
		</div>

		<div id="header">
				<h1>wicked jukebox</h1>
				<h2>hei spillt d'mus&eacute;k</h2>
		</div>

		<div id="content">
<!--
				<img src="images/logo.jpg" alt="Your Logo" class="logo" />

				<p class="introduction">
						Hello and welcome to Plain version 1.0. This is a simple web site template maximising the use of css and xhtml. Whitespace is used in abundance to really push its importance in web design. Navigate the page via the menu at the top of the page, or the links underneath this paragraph.
				</p>
-->

				<div id="sidebar">
          <div id="controls">
          {if $CORE->user_id ne '-1'}
          <a href="#" onclick="javascript:control('stop');" id="control_stop">&nbsp;</a>
          <a href="#" onclick="javascript:control('pause');" id="control_pause">&nbsp;</a>
          <a href="#" onclick="javascript:control('play');" id="control_play">&nbsp;</a>
          <a href="#" onclick="javascript:control('next');" id="control_next">&nbsp;</a>
          {/if}
          </div>

					<h1>Search</h1>
					<form name="searchform" onsubmit="return search();">
					<input type="text" name="pattern" /><br />
					<select name="mode">
            <option value="any">Any</option>
            <option value="artist">Artist</option>
            <option value="album">Album</option>
            <option value="song">Song</option>
          </select>
					<input type="submit" value="Find!"  />
          </form>

          <div id="login">
          <img src="/images/carousel.gif" width="0" height="0" />
          <img src="/images/tick.png" width="0" height="0" />
          <img src="/images/exclamation.png" width="0" height="0" />
          {if $CORE->user_id eq '-1'}
          {include file='login.tpl'}
          {else}
          {include file='profile.tpl'}
          {/if}
          </div>

					<div class="submenu" id="queue">
					{include file='queue.tpl'}
					</div>


				</div>

				<div id="mainbar">

		  {if $BODY_TEMPLATE ne ''}
	      {include file=$BODY_TEMPLATE}
	      {/if}

      <p>&nbsp;</p>
      <p>&nbsp;</p>
      <p>&nbsp;</p>
		  </div>

  </div>
  <div style="height: 50px; clear:both;">&nbsp;</div>
  <div id="footer">
 		wicked jukebox 2.o<br />
  Designed by <a href="http://www.jameskoster.co.uk">James Koster</a>, all the rest by exhuma.twn & doc.twn - The Wicked Net</div>
 </center>

</div>
</body>
</html>