<?php

namespace Jukebox;

use Zend\Mvc\ModuleRouteListener;
use Zend\Mvc\MvcEvent;

class Module
{

    public function onBootstrap(MvcEvent $e)
    {


    }

    public function getConfig()
    {
        return include __DIR__ . '/config/module.config.php';
    }

    public function getAutoloaderConfig()
    {
        return array(
            'Zend\Loader\StandardAutoloader' => array(
                'namespaces' => array(
                    __NAMESPACE__ => __DIR__ . '/src/' . __NAMESPACE__,
                ),
            ),
        );
    }
    public function getServiceConfig()
    {
        return array(
            'factories' => array(
                'jukebox.service.song' => function ($sm) {
                        return new \Jukebox\Service\Song(
                            $sm->get('doctrine.entitymanager.orm_default')
                        );
                    },
                'jukebox.service.artist' => function ($sm) {
                        return new \Jukebox\Service\Artist(
                            $sm->get('doctrine.entitymanager.orm_default')
                        );
                    },
                'jukebox.service.album' => function ($sm) {
                        return new \Jukebox\Service\Album(
                            $sm->get('doctrine.entitymanager.orm_default')
                        );
                    },
                'jukebox.service.channel' => function ($sm) {
                        return new \Jukebox\Service\Channel(
                            $sm->get('doctrine.entitymanager.orm_default')
                        );
                    },
                'jukebox.service.queue' => function ($sm) {
                        return new \Jukebox\Service\Queue(
                            $sm->get('doctrine.entitymanager.orm_default')
                        );
                    },
            )
        );

    }

}