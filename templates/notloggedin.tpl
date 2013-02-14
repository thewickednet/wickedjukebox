<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">

<!-- Web Page Design by James Koster - http://www.jameskoster.co.uk -->

<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Wicked Jukebox 2.o</title>
<link href="/style.css" rel="stylesheet" type="text/css" />
<link rel="shortcut icon" href="http://wickedjukebox.com/favicon.png" type="image/x-icon">
<link rel="icon" href="http://wickedjukebox.com/favicon.png" type="image/x-icon"> {literal}
  <script src="/javascript/google-jsapi.js" type="text/javascript"></script>
<script>
  google.load("jquery", "1.4.2");
</script>
  <script type="text/javascript" src="/javascript/jquery.ez-pinned-footer.js"></script>
{/literal}
</head>

<body>

<div id="container">
<a name="top" id="top"></a>
<center>
		<div id="menu">
                    &nbsp;
        </div>


    
    
        <div id="loginlogo">
				<h1><img src="/images/jukebox_logo.jpg" /></h1>
            </div>
    
    
        <div id="loginform">
            
          <form name="loginform" method="post" action="/auth/">
          {if $AUTH_ERROR ne ''}
          <img src="/images/exclamation.png" /> {$AUTH_ERROR}<br />
          {/if}
          <input type="text" name="username" value="{$AUTH_USER}" />
          <br />
          <input name="password" type="password" value="" />
          <input type="submit" value="Log In" />
          </form>
          <script>
          document.loginform.username.focus();
          </script>

        </div>
        
		<div id="content">

				<div id="sidebar">
          

				</div>

				<div id="mainbar">
				<div id="helper">
				
				</div>
				<div id="body">

                                
                                
                                </div>
		  </div>
  </div>
  <div style="height: 50px; clear:both;">&nbsp;</div>
  <div id="footer">
 		wicked jukebox 2.o<br />
  Design based on <a href="http://www.oswd.org/design/preview/id/2087" target="_blank">Plain 1.0</a> by <a href="http://www.jameskoster.co.uk" target="_blank">James Koster</a> - Logo by <a href="http://www.koreatabs.de" target="_blank">Jens Lumm</a> - all the rest by exhuma.twn & doc.twn - <a href="http://www.wicked.lu" target="_blank">The Wicked Net</a></div>
 </center>
{literal}
<script>
$(document).ready(function() {
    $("#footer").pinFooter();
});

$(window).resize(function() {
    $("#footer").pinFooter();
});
</script>
{/literal}
</div>
</body>
</html>
