<?php

// Define path to application directory
defined('APPLICATION_PATH')
    || define('APPLICATION_PATH', realpath(dirname(__FILE__) . '/../application'));

// Define path to application directory
defined('APPLICATION_ROOT')
    || define('APPLICATION_ROOT', realpath(dirname(__FILE__) . '/../'));

// Define application environment
defined('APPLICATION_ENV')
    || define('APPLICATION_ENV', (getenv('APPLICATION_ENV') ? getenv('APPLICATION_ENV') : 'production'));

// Ensure library/ is on include_path
set_include_path(implode(PATH_SEPARATOR, array(
    realpath(APPLICATION_PATH . '/../library'),
    realpath(APPLICATION_PATH . '/../vendor')
)));

/** Zend_Application */
require_once 'Zend/Application.php';

// Creating application
$application = new Zend_Application(
    APPLICATION_ENV,
    APPLICATION_PATH . '/configs/application.ini'
);

// Bootstrapping resources
$bootstrap = $application->bootstrap()->getBootstrap();

$options = $bootstrap->getOptions();
$presets = $options['wjb']['images']['preset'];

$artistService = new \WJB\Service\Artist();
$albumService = new \WJB\Service\Album();

$image = new \WJB\Image();
$image->setDisplayOutput(false);
$image->setResetSource(false);

foreach ($artistService->getAll() as $artist)
{
    $sourceFilename = $artist->getPictureFile();
    if ($sourceFilename == false)
        continue;
    $image->setSource($sourceFilename);
    foreach ($presets['artist'] as $prestName => $prestDim)
    {
        $destPath = sprintf("%s/public/images/artist/%s/", rtrim(APPLICATION_ROOT, '/'), $prestName);

        if (!is_dir($destPath))
            mkdir ($destPath, 0775, true);

        $destFile = $destPath . $artist->getId() . '.png';
        $image->setPreset($prestDim);
        $image->setDestination($destFile);
        $image->generate_image_thumbnail();
    }
}



foreach ($albumService->getAll() as $album)
{
    $sourceFilename = $album->getPictureFile();
    if ($sourceFilename == false)
        continue;
    $image->setSource($sourceFilename);
    foreach ($presets['album'] as $prestName => $prestDim)
    {
        $destPath = sprintf("%s/public/images/album/%s/", rtrim(APPLICATION_ROOT, '/'), $prestName);

        if (!is_dir($destPath))
            mkdir ($destPath, 0775, true);

        $destFile = $destPath . $album->getId() . '.png';
        $image->setPreset($prestDim);
        $image->setDestination($destFile);
        $image->generate_image_thumbnail();
    }
}

