<?php

class ImagesController extends Zend_Controller_Action
{

    private $_image;
    private $_config;

    private $_id;
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
        $this->_id = str_replace('.png', '', $this->getRequest()->getParam('id'));

        $options = $bootstrap->getOptions();
        $this->_config = $options['wjb']['images'];

        $this->_preset_dim = $this->_config['preset'][$this->_category][$this->_preset];

        $this->_image = new \WJB\Image();

        switch ($this->_category)
        {
            case "album":
                $albumService = new \WJB\Service\Album();
                $album = $albumService->getById($this->_id);
                $filename = $album->getPictureFile();
            break;
            case "artist":
                $artistService = new \WJB\Service\Artist();
                $artist = $artistService->getById($this->_id);
                $filename = $artist->getPictureFile();
            break;
        }


        if (!$filename)
        {
            switch($this->_category)
            {
                case "album":
                    $this->_image->setWriteFile(false);
                    $this->_srcFilename = $this->_config['placeholder']['channel'];
                    break;
                case "artist":
                    $this->_image->setWriteFile(false);
                    $this->_srcFilename = $this->_config['placeholder']['bouquet'];
                    break;
                default:
                    $this->_image->setWriteFile(false);
                    $this->getResponse()
                        ->setHttpResponseCode(404);
                    die();
            }
        }

        $this->_image->setSource($filename);


    }


    public function renderAction()
    {

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
            $destPath = sprintf("%s/public/images/%s/%s/", rtrim(APPLICATION_ROOT, '/'), trim($this->_category, '/'), trim($this->_preset, '/'));

            if (!is_dir($destPath))
                mkdir ($destPath, 0775, true);

            $destFile = $destPath . $this->_id . '.png';

            $this->log->info(sprintf("RENDERING source: %s -> destination: %s", $this->_srcFilename, $destFile));

            $this->_image->setPreset($this->_preset_dim);
            $this->_image->setDestination($destFile);
            $this->_image->generate_image_thumbnail();
            exit();
        }

    }

}
