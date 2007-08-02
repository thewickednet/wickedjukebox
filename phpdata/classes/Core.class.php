<?php

class Core {

    public $display = true;
    public $template = "base.tpl";
    public $userinfo = array();
    public $permissions = array();
    public $user_id = -1;
    public $channel_id = -1;
    

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
    
}

?>