<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */


  $smarty->assign("USER_PLAYS", User::getPlays());
  $smarty->assign("USER_DOWNLOADS", User::getDownloads());
  $smarty->assign("USER_SKIPS", User::getSkips());


  $smarty->assign("ALBUM_PLAYS", Album::getPlays());
  $smarty->assign("ALBUM_DOWNLOADS", Album::getDownloads());

  $smarty->assign("SONG_PLAYS", Song::getPlays());
  $smarty->assign("SONG_DOWNLOADS", Song::getDownloads());
  $smarty->assign("SONG_SKIPS", Song::getSkips());

  $body_template = 'stats.tpl';

?>