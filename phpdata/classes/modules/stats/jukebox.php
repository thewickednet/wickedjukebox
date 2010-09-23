<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */


  $smarty->assign("SONG_TOTAL", Song::getTotalCount());
  $smarty->assign("SONG_SIZE", Song::getTotalSize());
  $smarty->assign("ALBUM_TOTAL", Album::getTotalCount());
  $smarty->assign("ARTIST_TOTAL", Artist::getTotalCount());
  $smarty->assign("USER_TOTAL", User::getTotalCount());
  $smarty->assign("USER_ACTIVE", User::getActive());
  $smarty->assign("USER_SHOUT", User::getShouts());

  
  $smarty->assign("USER_PLAYS", User::getPlays());
  $smarty->assign("USER_DOWNLOADS", User::getDownloads());

  $smarty->assign("ARTIST_SONGS", Artist::getSongCount());
  $smarty->assign("ARTIST_ALBUMS", Artist::getAlbumCount());
  
  $smarty->assign("SONGS_LOVE", Song::getStandingCount('love'));
  $smarty->assign("SONGS_HATE", Song::getStandingCount('hate'));
  
  

  $smarty->assign("ALBUM_PLAYS", Album::getPlays());
//  $smarty->assign("ALBUM_DOWNLOADS", Album::getDownloads());

  $smarty->assign("SONG_PLAYS", Song::getPlays());

  $body_template = 'stats/jukebox.tpl';

?>