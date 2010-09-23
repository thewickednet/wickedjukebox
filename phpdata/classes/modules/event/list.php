<?php 


$events = Event::getPast();


$smarty->assign("EVENTS_PAST", $events);

$body_template = "event/list.tpl";