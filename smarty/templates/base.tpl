<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">

<!-- Web Page Design by James Koster - http://www.jameskoster.co.uk -->

<head>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
<title>Wicked Jukebox</title>
<link href="/css/1.css" rel="stylesheet" type="text/css" />
{literal}
  <script type="text/javascript" src="/javascript/prototype.js"></script>
  <script type="text/javascript" src="/javascript/ajax.js"></script>
  <script type="text/javascript" src="/javascript/jukebox.js"></script>
  <script>
  setInterval('refreshQueue()', 15000);
  </script>

{/literal}
</head>

<body onload="refreshQueue();">
<div id="hiddenDiv" style="position:absolute; visibility:hidden; z-index:1000"></div>
<div id="container">
<a name="top" id="top"></a>
<center>
		<div id="menu">
				<a href="/browse/artists/">artists</a> <a href="/browse/albums/">albums</a> <a href="/browse/genres/">genres</a> <a href="/browse/latest/">latest additions</a> <a href="/stats/">statistics</a> <a href="/admin/">admin</a>
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

          <a href="#" onclick="javascript:control('prev');"><img src="/images/c_prev.gif" border="0" /></a>
          <a href="#" onclick="javascript:control('rewind');"><img src="/images/c_rw.gif" border="0" /></a>
          <a href="#" onclick="javascript:control('stop');"><img src="/images/c_stop.gif" border="0" /></a>
          <a href="#" onclick="javascript:control('pause');"><img src="/images/c_pause.gif" border="0" /></a>
          <a href="#" onclick="javascript:control('play');"><img src="/images/c_play.gif" border="0" /></a>
          <a href="#" onclick="javascript:control('forward');"><img src="/images/c_ff.gif" border="0" /></a>
          <a href="#" onclick="javascript:control('next');"><img src="/images/c_next.gif" border="0" /></a>

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
          {if count($USERINFO) eq '0'}
          {include file='login.tpl'}
          {else}
          {include file='profile.tpl'}
          {/if}
          </div>
						<h1>Queue</h1>
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
  <div style="height: 50px;">&nbsp;</div>
  <div id="footer">
 		wicked jukebox 1.0<br />
  Designed by <a href="http://www.jameskoster.co.uk">James Koster</a>, all the rest by exhuma.twn & doc.twn - The Wicked Net</div>
 </center>

</div>
</body>
</html>
