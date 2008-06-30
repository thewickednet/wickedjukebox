<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">

<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Wicked Jukebox 2.o</title>
<link href="/style.css" rel="stylesheet" type="text/css" />
{literal}
  <script type="text/javascript" src="/javascript/prototype.js"></script>
  <script type="text/javascript" src="/javascript/jukebox.js"></script>
  <script type="text/javascript" src="/audio-player/audio-player.js"></script>  
{/literal}
</head>
<body onload="javascript:refreshPlayerPeriodical();">

{literal}
&nbsp;<br />
<div align="center">
         <script type="text/javascript">  
             AudioPlayer.setup("/audio-player/player.swf", {  
                 width: 250  
             });  
         </script>
          <p id="audioplayer_1"></p>  
         <script type="text/javascript">  
         AudioPlayer.embed("audioplayer_1", {soundFile: "http://wicked.lu:8001/wicked.mp3", autostart: "yes", titles: "Wicked Jukebox"});  
         </script>
{/literal}
&nbsp;<br />
&nbsp;<br />
</div>
<div id="playerInfo" class="submenu">
{include file='player/info.tpl'}
</div>
</body>
</html>
