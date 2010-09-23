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

    function buildAlphaList() {
        
        $alpha = array(
                       'num'    =>  '0-9',
                       'a'      =>  'A',
                       'b'      =>  'B',
                       'c'      =>  'C',
                       'd'      =>  'D',
                       'e'      =>  'E',
                       'f'      =>  'F',
                       'g'      =>  'G',
                       'h'      =>  'H',
                       'i'      =>  'I',
                       'j'      =>  'J',
                       'k'      =>  'K',
                       'l'      =>  'L',
                       'm'      =>  'M',
                       'n'      =>  'N',
                       'o'      =>  'O',
                       'p'      =>  'P',
                       'q'      =>  'Q',
                       'r'      =>  'R',
                       's'      =>  'S',
                       't'      =>  'T',
                       'u'      =>  'U',
                       'v'      =>  'V',
                       'w'      =>  'W',
                       'x'      =>  'X',
                       'y'      =>  'Y',
                       'z'      =>  'Z'
                        );
        return $alpha;
        
    }

    function highLight($params, &$smarty) {
        
//        $replace = sprintf("<span class=\"highlight\">%s</span>", $params['mask']);
        $search = $params['mask'];
        return preg_replace("/$search/im", '<span class=highlight>$0</span>', $params['string']);
        
    }

    function escapeDoubleQuotes($string) {
        
        return str_replace('"', '\"', $string);
        
    }

    function url2link($text) {
		$text = preg_replace('/(http:\/\/|ftp:\/\/)([^\s,]*)/i','<a href="$1$2" target="_blank">$1$2</a>',$text);
		$text = preg_replace('/([^"])([A-Z0-9._%-]+@[A-Z0-9.-]+\.[A-Z]{2,4})/i','$1<a href="mailto:$2">$2</a>',$text);
      
       return $text;
    }
}


