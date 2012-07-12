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
$search = $options['lucene'];


// Retrieve Doctrine Container resource
$container = $bootstrap->getResource('doctrine');

set_time_limit(0);
error_reporting(0);

$index = Zend_Search_Lucene::create($search['index_path']);

$artistService = new \WJB\Service\Artist();
$songService = new \WJB\Service\Song();
$albumService = new \WJB\Service\Album();
$i = 0;

$artists = $artistService->getAll();
$songs = $songService->getAll();
$albums = $albumService->getAll();

$total = count($songs) + count($artists) + count($albums);

foreach ($artists as $artist)
{

    $doc = new Zend_Search_Lucene_Document();

    $doc->addField(Zend_Search_Lucene_Field::Keyword('class', 'artist'));
    $doc->addField(Zend_Search_Lucene_Field::Keyword('type', 'artist'));
    $doc->addField(Zend_Search_Lucene_Field::Keyword('country', $artist->getCountryCode()));
    $doc->addField(Zend_Search_Lucene_Field::UnIndexed('key', $artist->getId()));
    $doc->addField(Zend_Search_Lucene_Field::Keyword('created', time()));
    $doc->addField(Zend_Search_Lucene_Field::UnIndexed('data', serialize($artist->toArray(true))));

    $doc->addField(Zend_Search_Lucene_Field::Text('artist', $artist->getName()));

    $index->addDocument($doc);

    $i++;
    unset($artist);

}

$index->commit();

printf("%d artists added to index\n", $i);
unset($artists);

$i = 0;
foreach ($songs as $song)
{

    $doc = new Zend_Search_Lucene_Document();

    $doc->addField(Zend_Search_Lucene_Field::Keyword('class', 'song'));
    $doc->addField(Zend_Search_Lucene_Field::Keyword('type', 'song'));
    $doc->addField(Zend_Search_Lucene_Field::UnIndexed('key', $song->getId()));
    $doc->addField(Zend_Search_Lucene_Field::UnIndexed('created', time()));
    $doc->addField(Zend_Search_Lucene_Field::Text('artist', $song->getArtist()->getName()));
    $doc->addField(Zend_Search_Lucene_Field::Unstored('lyrics', $song->getLyrics()));
    $doc->addField(Zend_Search_Lucene_Field::UnIndexed('data', serialize($song->toArray(true))));

    $doc->addField(Zend_Search_Lucene_Field::Text('song', $song->getTitle()));
    $doc->addField(Zend_Search_Lucene_Field::Text('duration', (int) $song->getDuration()));

    $index->addDocument($doc);

    $i++;
    unset($song);

}

$index->commit();

printf("%d songs added to index\n", $i);
unset($songs);

$i = 0;

foreach ($albums as $album)
{

    $doc = new Zend_Search_Lucene_Document();


    $doc->addField(Zend_Search_Lucene_Field::Keyword('class', 'album'));
    $doc->addField(Zend_Search_Lucene_Field::Keyword('type', 'album'));
    $doc->addField(Zend_Search_Lucene_Field::UnIndexed('key', $album->getId()));
    $doc->addField(Zend_Search_Lucene_Field::UnIndexed('created', time()));
    $doc->addField(Zend_Search_Lucene_Field::Text('artist', $album->getArtist()->getName()));
    $doc->addField(Zend_Search_Lucene_Field::UnIndexed('data', serialize($album->toArray(true))));

    $doc->addField(Zend_Search_Lucene_Field::Text('album', $album->getName()));

    if ($album->getReleaseDate() != null)
        $doc->addField(Zend_Search_Lucene_Field::Text('year', $album->getReleaseDate()->format('Y')));

    $index->addDocument($doc);

    $i++;

}
$index->commit();

printf("%d albums added to index\n", $i);


$index->optimize();
