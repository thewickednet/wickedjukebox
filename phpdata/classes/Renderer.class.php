<?php

class Renderer {
    
    private $src_image      = null;
    private $src_mime       = null;
    private $src_w          = 0;
    private $src_h          = 0;
    private $src_bits       = 0;
    private $src_channels   = 0;

    public  $out_wmax       = 0;
    public  $out_hmax       = 0;

    private $out_image      = null;
    public  $out_mime       = "image/png";
    public  $out_quality    = 75;
    
    public  $out_file		= "dummy";
    
    public $true_color      = false;
    
    private $preset         = null;
    

    function __construct($category, $preset, $filename = "") {
        
        $this->preset = $this->getPreset($category, $preset);
        
        if (count($this->preset) == 0)
            die("invalid request - preset empty");
        
        
        if (!empty($filename))
            $src_file = $filename;
        elseif ($this->preset['placeholder'] != '') {
            $src_file = sprintf("../httpd_data/placeholder/%s", $this->preset['placeholder']);
            if (!file_exists($src_file))
                $src_file = sprintf("../httpd_data/placeholder/%s", $this->preset['placeholder']);
        } else 
                die("invalid request");
        //print($src_file);
        //print_r($info);
        $info = getimagesize($src_file);

        $this->out_wmax     = $this->preset['wmax'];
        $this->out_hmax     = $this->preset['hmax'];
        $this->noproportion = $this->preset['noproportion'];
        $this->force_mime   = $this->preset['force_mime'];
        
        $this->src_w        = $info[0];
        $this->src_h        = $info[1];
        $this->src_channels = $info[2];
        $this->src_bits     = $info['bits'];
        $this->src_mime     = $info['mime'];

        switch($this->src_mime) {
          case "image/jpg":
          case "image/jpeg":
            $this->src_image = imagecreatefromjpeg($src_file);
          break;
          case "image/gif":
            $this->src_image = imagecreatefromgif($src_file);
          break;
          case "image/png":
            $this->src_image = imagecreatefrompng($src_file);
          break;
          default:
            die("input format not supported");
        }
        
    }
    
    function render() {

        $w_max = $this->out_wmax;
        $h_max = $this->out_hmax;
        $prop  = $this->noproportion;
        
        if ($prop && $w_max == $h_max) {
            
              $format_final_w = $w_max;
              $format_final_h = $h_max;
            
        } else {
            $proportion = $this->src_w / $this->src_h;
            $w_potentiel = $h_max * $proportion;
            $h_potentiel = $w_max / $proportion;
            if ($w_potentiel <= $w_max) {
              $format_final_w = $w_potentiel;
              $format_final_h = $h_max;
            } elseif ($h_potentiel <= $h_max) {
              $format_final_w = $w_max;
              $format_final_h = $h_potentiel;
            }
        }

        if ($this->true_color)
            $image_p = imagecreatetruecolor($format_final_w, $format_final_h);
        else 
            $image_p = imagecreate($format_final_w, $format_final_h);

        imagecopyresampled($image_p, $this->src_image, 0, 0, 0, 0, $format_final_w, $format_final_h, $this->src_w, $this->src_h);

        if (!empty($this->force_mime))
            $this->out_mime = $this->force_mime;
        
        switch($this->out_mime) {
          case "image/jpeg":
    		header('Content-Disposition: inline; filename="'.$this->out_file.'.jpg"');
            header("Content-type: image/jpeg");
            imagejpeg($image_p, "", $this->out_quality);
          break;
          case "image/gif":
    		header('Content-Disposition: inline; filename="'.$this->out_file.'.gif"');
            header("Content-type: image/gif");
            imagegif($image_p);
          break;
          case "image/png":
    		header('Content-Disposition: inline; filename="'.$this->out_file.'.png"');
            header("Content-type: image/png");
            imagepng($image_p);
          break;
          default:
            die("output format not supported");
        }

    }

    function getPreset($category, $preset) {

        $db = Zend_Registry::get('database');
        
        $select = $db->select()
                     ->from('render_presets')
                     ->where('category = ?', $category)
                     ->where('preset = ?', $preset);
                     
        $stmt = $select->query();
        $result = $stmt->fetchAll();
        if (count($result) == 1)
            return $result[0];
        return array();
    }

}

?>