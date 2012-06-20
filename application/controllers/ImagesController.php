<?php

class ImagesController extends Zend_Controller_Action
{

    private $_image;
    private $_config;

    private $_filename;
    private $_srcFilename;

    private $_preset_dim;
    private $_category;
    private $_preset;

    public $log;


    public function init()
    {
        $this->_helper->viewRenderer->setNoRender(true);

        $this->log = Zend_Registry::get('log');

        $bootstrap = Zend_Controller_Front::getInstance()->getParam('bootstrap');
        $this->_category = $this->getRequest()->getParam('category');
        $this->_preset = $this->getRequest()->getParam('preset');
        $this->_filename = $this->getRequest()->getParam('filename');

        $options = $bootstrap->getOptions();
        $this->_config = $options['images'][$this->_category];

        $imagePath = sprintf("%s/%s/", rtrim($this->_config['srcpath'], '/'), $this->_category);

        if (!is_dir($imagePath) && !is_readable($imagePath))
        {
            $this->getResponse()
                ->setHttpResponseCode(500);
            die("not readable: " . $imagePath);
        }

        if ($this->_preset == 'original')
        {
            $requestId = $this->getRequest()->getParam('original');
            $file = Application_Model_Image::getSourceFilename($this->_category, $this->_filename);
        }
        else
        {
            $file = Application_Model_Image::getSourceFilename($this->_category, $this->_filename);

            if (!$file)
            {
                $this->getResponse()
                    ->setHttpResponseCode(404);
                die("not found in database");
            }
            $this->_preset_dim = $this->_config['preset'][$this->_preset];
        }
        $this->_srcFilename =  $imagePath . $file;
        if (!file_exists($this->_srcFilename))
        {
            switch($this->_category)
            {
                case "channel":
                    $this->_srcFilename = $this->_config['placeholder']['channel'];
                    break;
                case "bouquet":
                    $this->_srcFilename = $this->_config['placeholder']['bouquet'];
                    break;
                default:
                    $this->getResponse()
                        ->setHttpResponseCode(404);
                    die();
            }
        }

    }


    public function renderAction()
    {

        $this->_image = new Model_Image($this->_srcFilename);

        $destPath = sprintf("%s/%s/%s/", rtrim($this->_config['destpath'], '/'), trim($this->_category, '/'), trim($this->_preset, '/'));
        if (!is_dir($destPath))
            mkdir ($destPath, 0775, true);

        if ($this->_preset == 'original')
        {
            $size = getimagesize($this->_srcFilename);
            $mime = $size['mime'];
            $this->log->info(sprintf("PASSTHRU: %s with Content-Type: %s", $this->_srcFilename, $mime));
            header("Content-type: " . $mime);
            readfile($this->_srcFilename);
        }
        else
        {
            $destFile = $destPath . $this->_filename;

            $this->log->info(sprintf("RENDERING source: %s -> destination: %s", $this->_filename, $destFile));
            $this->_image->setPreset($this->_preset_dim);
            $this->_image->setDestination($destFile);
            $this->_image->generate_image_thumbnail();
        }

    }

}
