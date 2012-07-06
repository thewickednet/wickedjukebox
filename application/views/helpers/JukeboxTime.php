<?php


class Zend_View_Helper_JukeboxTime extends Zend_View_Helper_Abstract
{

    public function jukeboxTime($time) {

        $result = "";

        $hours = floor($time/3600);
        $minutes = floor(($time - $hours*3600)/60);
        $seconds = floor($time - ($hours*3600 + $minutes*60));

        if ($hours)
            $result = sprintf("%02d:", $hours);

        $result .= sprintf("%02d:%02d", $minutes, $seconds);

        return $result;

    }
}
