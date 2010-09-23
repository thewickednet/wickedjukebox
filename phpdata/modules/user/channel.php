<?php

$_SESSION['channel_id'] = $_GET['id'];

User::set(array('channel_id' => $_GET['id']), $core->user_id);

header("Location: " . $_SERVER["HTTP_REFERER"]);
