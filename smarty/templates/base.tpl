<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">


<!-- Web Page Design by James Koster - http://www.jameskoster.co.uk -->


<head>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
<title>Wicked Jukebox</title>
<link href="/css/1.css" rel="stylesheet" type="text/css" />
</head>

<body>
<a name="top" id="top"></a>
<center>
		<div id="menu">
				<a href="/browse/albums/">albums</a> <a href="/browse/artists/">artists</a> <a href="/browse/genres/">genres</a> <a href="/browse/latest/">latest additions</a> <a href="/admin/">admin</a>
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
					<h1>Search</h1>
					<form>
					<input type="text" value="" name="pattern" />
					<br />
					<input type="submit" value="Find!" />
          </form>

					<h1>Log In</h1>
					<input type="text" value="Username" />
					<br />
					<input name="" type="password" value="Password" />
					<br />
					<input type="button" value="Log In" />


						<h1>Queue</h1>
						<div class="submenu">
            {foreach from=$QUEUE item=QUEUE_SONG}
								<a href="#top">{$QUEUE_SONG}</a>
            {/foreach}
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
  <div id="footer">
  		wicked jukebox 1.0<br />
  Designed by <a href="http://www.jameskoster.co.uk">James Koster</a>, all the rest &copy; The Wicked Net</div>
</center>
</body>
</html>
