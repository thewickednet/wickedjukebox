<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */


function bytesToHumanReadable($bytes)
{
   if (!is_numeric($bytes) || $bytes < 0) {
       return false;
   }

   for ($level = 0; $bytes >= 1024; $level++) {
       $bytes /= 1024;
   }

   switch ($level)
   {
       case 0:
           $suffix = (isset($names[0])) ? $names[0] : 'Bytes';
           break;
       case 1:
           $suffix = (isset($names[1])) ? $names[1] : 'KB';
           break;
       case 2:
           $suffix = (isset($names[2])) ? $names[2] : 'MB';
           break;
       case 3:
           $suffix = (isset($names[3])) ? $names[3] : 'GB';
           break;
       case 4:
           $suffix = (isset($names[4])) ? $names[4] : 'TB';
           break;
       default:
           $suffix = (isset($names[$level])) ? $names[$level] : '';
           break;
   }

   if (empty($suffix)) {
       trigger_error('Unable to find suffix for case ' . $level);
       return false;
   }

   return round($bytes, $precision) . ' ' . $suffix;
}

$smarty->register_modifier('bytesToHumanReadable', 'bytesToHumanReadable');


?>