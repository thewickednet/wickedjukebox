<?php

class Model_Image
{

    private $_max_width = 150;
    private $_max_height = 150;

    private $_src_width = false;
    private $_src_height = false;
    private $_src_image_type = false;

    private $_src_gd_image = false;

    private $_target_image = null;
    private $_quality = 90;

    public function __construct($sourceImage) {

        list( $this->_src_width, $this->_src_height, $this->_src_image_type ) = getimagesize( $sourceImage );

        switch ( $this->_src_image_type )
        {
            case IMAGETYPE_GIF:
                $this->_src_gd_image = imagecreatefromgif( $sourceImage );
                break;

            case IMAGETYPE_JPEG:
                $this->_src_gd_image = imagecreatefromjpeg( $sourceImage );
                break;

            case IMAGETYPE_PNG:
                $this->_src_gd_image = imagecreatefrompng( $sourceImage );
                break;
        }

        if ( $this->_src_gd_image === false )
        {
            return false;
        }

        return true;

    }

    public function setPreset($preset)
    {
        list ($dimensions, $quality) = explode(",", trim($preset));
        if (isset($quality) && is_numeric($quality))
            $this->setQuality($quality);
        list ($this->_max_width, $this->_max_height) = explode("x", $dimensions);
    }

    public function setDestination($path)
    {
        $this->_target_image = $path;
    }

    public function setQuality($quality)
    {
        $this->_quality = $quality;
    }

    public function generate_image_thumbnail()
    {

        $thumbnail_image_width = $this->_max_width;
        $thumbnail_image_height = $this->_max_height;

        $source_image_width = $this->_src_width;
        $source_image_height = $this->_src_height;

        $source_aspect_ratio = $source_image_width / $source_image_height;
        $thumbnail_aspect_ratio = $thumbnail_image_width / $thumbnail_image_height;

        if ( $source_image_width <= $thumbnail_image_width && $source_image_height <= $thumbnail_image_height )
        {
            $thumbnail_image_width = $source_image_width;
            $thumbnail_image_height = $source_image_height;
        }
        elseif ( $thumbnail_aspect_ratio > $source_aspect_ratio )
        {
            $thumbnail_image_width = ( int ) ( $thumbnail_image_height * $source_aspect_ratio );
        }
        else
        {
            $thumbnail_image_height = ( int ) ( $thumbnail_image_width / $source_aspect_ratio );
        }

        $thumbnail_gd_image = imagecreatetruecolor( $thumbnail_image_width, $thumbnail_image_height );
        imagealphablending( $thumbnail_gd_image, false );
        imagesavealpha( $thumbnail_gd_image, true );

        imagecopyresampled($thumbnail_gd_image, $this->_src_gd_image, 0, 0, 0, 0, $thumbnail_image_width, $thumbnail_image_height, $this->_src_width, $this->_src_height);

        header("Content-Type: image/png");
        imagepng($thumbnail_gd_image, $this->_target_image, $this->_quality);

        imagedestroy($this->_src_gd_image);

        imagedestroy($thumbnail_gd_image);

        readfile($this->_target_image);

        return true;
    }

    public static function getSourceFilename($category, $id)
    {
        return $id;
    }

}
