<?php

class Core {

    public $display = true;
    public $template = "base.tpl";
    public $userdata = array();
    public $permissions = array();
    public $user_id = -1;
    public $channel_id = -1;
    public $active_node = "";
    

    function __construct($demon_config) {
        
        if (isset($_SESSION['channel_id']))
            $this->channel_id = $_SESSION['channel_id'];
        else {
            $channel = Channel::getByName($demon_config->default_channel);
            $this->channel_id = $channel['id'];
            $_SESSION['channel_id'] = $channel['id'];
        }

    }
    
    function printr($message) {

        printf("<pre>\n%s\n</pre>\n", print_r($message, true));

    }

    function reIndex($input = array(), $index_field = 0, $valueField = "") {
        
        $output = array();
        
        foreach ($input as $entry) {
            if (!empty($valueField))
                $output[$entry[$index_field]] = $entry[$valueField];
            else 
                $output[$entry[$index_field]] = $entry;
        }
        return $output;
        
    }
        
    function bytesToHumanReadable($bytes) {
    
      $precision = 2;
    
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

}

?>