<?php

class Core {

    public $display = true;
    public $template = "base.tpl";
    public $userinfo = array();
    public $permissions = array();
    public $user_id = 0;

    static private $instance = false;

    static function instance() {
        if(!Core::$instance) {
            Core::$instance = new Core();
        }
        return Core::$instance;
    }

    function printr($message) {

        printf("<pre>\n%s\n</pre>\n", print_r($message, true));

    }

}

?>