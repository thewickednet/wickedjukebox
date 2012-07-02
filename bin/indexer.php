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

// Retrieve Doctrine Container resource
$container = $bootstrap->getResource('doctrine');

$index = Zend_Search_Lucene::create(APPLICATION_ROOT . '/data/lucence');


$artistService = new \WJB\Service\Artist();
$songService = new \WJB\Service\Song();
$albumService = new \WJB\Service\Album();
$i = 0;

foreach ($artistService->getAll() as $artist)
{

    $doc = new Zend_Search_Lucene_Document();

    $doc->addField(Zend_Search_Lucene_Field::UnIndexed('class', 'artist'));
    $doc->addField(Zend_Search_Lucene_Field::UnIndexed('key', $artist->getId()));
    $doc->addField(Zend_Search_Lucene_Field::Keyword('created', time()));

    $doc->addField(Zend_Search_Lucene_Field::Text('artist_name', $artist->getName()));

    $index->addDocument($doc);

    $i++;

}

$index->commit();

printf("%d artists added to index\n", $i);

$i = 0;
foreach ($songService->getAll() as $song)
{

    $doc = new Zend_Search_Lucene_Document();

    $doc->addField(Zend_Search_Lucene_Field::UnIndexed('class', 'song'));
    $doc->addField(Zend_Search_Lucene_Field::UnIndexed('key', $song->getId()));
    $doc->addField(Zend_Search_Lucene_Field::UnIndexed('created', time()));
    $doc->addField(Zend_Search_Lucene_Field::UnIndexed('artist_name', $song->getArtist()->getName()));
    $doc->addField(Zend_Search_Lucene_Field::Unstored('lyrics', $song->getLyrics()));

    $doc->addField(Zend_Search_Lucene_Field::Text('song_title', $song->getTitle()));

    $index->addDocument($doc);

    $i++;

}

$index->commit();

printf("%d songs added to index\n", $i);

$i = 0;

foreach ($albumService->getAll() as $album)
{

    $doc = new Zend_Search_Lucene_Document();

    $doc->addField(Zend_Search_Lucene_Field::UnIndexed('class', 'album'));
    $doc->addField(Zend_Search_Lucene_Field::UnIndexed('key', $song->getId()));
    $doc->addField(Zend_Search_Lucene_Field::UnIndexed('created', time()));
    $doc->addField(Zend_Search_Lucene_Field::UnIndexed('artist_name', $album->getArtist()->getName()));

    $doc->addField(Zend_Search_Lucene_Field::Text('album_name', $album->getName()));

    $index->addDocument($doc);

    $i++;

}
$index->commit();

printf("%d albums added to index\n", $i);


$index->optimize();
