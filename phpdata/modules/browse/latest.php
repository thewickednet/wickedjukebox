<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */


  $results = Song::getLatest();

  $smarty->assign("SONGS", $results);

  $body_template = 'browse/latest.tpl';


?>
