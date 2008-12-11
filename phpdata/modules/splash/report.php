<?php

	$_GET['song'] = $_GET['param'];
	include "../phpdata/modules/song/report.php";

	$core->template = 'splash/nowplaying.tpl';
	
?>