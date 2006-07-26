<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */



  switch($_GET['mode']){
    case "clean":

      $queue->clean();

      break;
  } // switch


?>