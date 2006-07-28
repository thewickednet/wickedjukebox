<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */



  $song = Song::getById($_GET['param']);

  if (isset($song['album_id'])) {
    $smarty->assign("ALBUM_COVER", Album::hasCover($song['album_id']));
    $smarty->assign("ALBUM", Album::getById($song['album_id']));
  }

  $smarty->assign("ARTIST_COVER", Artist::hasCover($song['artist_id']));

  $smarty->assign("SONG", $song);

  $body_template = 'details/song.tpl';


?>