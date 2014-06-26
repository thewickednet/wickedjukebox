<?php
/**
 * Zend Framework (http://framework.zend.com/)
 *
 * @link      http://github.com/zendframework/ZendSkeletonApplication for the canonical source repository
 * @copyright Copyright (c) 2005-2014 Zend Technologies USA Inc. (http://www.zend.com)
 * @license   http://framework.zend.com/license/new-bsd New BSD License
 */

return array(
    'router' => array(
        'routes' => array(
        ),
    ),
    'service_manager' => array(
    ),
    'controllers' => array(
        'invokables' => array(
        ),
    ),
    'view_manager' => array(
        'template_path_stack' => array(
            __DIR__ . '/../view',
        ),
        'strategies' => array(
            'ViewJsonStrategy'
        )
    ),
    'doctrine' => array(
        'driver' => array(
            'jukebox_entity' => array(
                'class' => 'Doctrine\ORM\Mapping\Driver\AnnotationDriver',
                'cache' => 'my_memcache',
                'paths' => __DIR__ . '/../src/Jukebox/Entity',
            ),

            'orm_default' => array(
                'drivers' => array(
                    'Jukebox\Entity' => 'jukebox_entity',

                ),
            ),
        ),
    ),
);
