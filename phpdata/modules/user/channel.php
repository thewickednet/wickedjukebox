<?php

$_SESSION['channel_id'] = $_GET['id'];

header("Location: " . $_SERVER["HTTP_REFERER"]);
