<?php
/**
 * Zend Framework (http://framework.zend.com/)
 *
 * @link      http://github.com/zendframework/ZendSkeletonApplication for the canonical source repository
 * @copyright Copyright (c) 2005-2013 Zend Technologies USA Inc. (http://www.zend.com)
 * @license   http://framework.zend.com/license/new-bsd New BSD License
 */

namespace Application;

use Zend\Mvc\ModuleRouteListener;
use Zend\Mvc\MvcEvent;

class Module
{
    protected $authWhitelist = array('zfcuser/login', 'zfcuser/register');

    public function onBootstrap(MvcEvent $e)
    {
        $eventManager        = $e->getApplication()->getEventManager();
        $moduleRouteListener = new ModuleRouteListener();
        $moduleRouteListener->attach($eventManager);
        $sm = $e->getApplication()->getServiceManager();

        $list = $this->authWhitelist;
        $auth = $sm->get('zfcuser_auth_service');

        $eventManager->attach(MvcEvent::EVENT_ROUTE, function(\Zend\Mvc\MvcEvent $e) use ($list, $auth) {

            $match = $e->getRouteMatch();
            // No route match, this is a 404
            if (!$match instanceof \Zend\Mvc\Router\Http\RouteMatch) {
                return;
            }

            // Route is whitelisted
            $name = $match->getMatchedRouteName();
            if (in_array($name, $list)) {
                return;
            }

            // User is authenticated
            if ($auth->hasIdentity()) {
                return;
            }

            // Redirect to the user login page, as an example
            $router   = $e->getRouter();
            $url      = $router->assemble(array(), array(
                'name' => 'zfcuser/login'
            ));

            $response = $e->getResponse();
            $response->getHeaders()->addHeaderLine('Location', $url);
            $response->setStatusCode(302);

            return $response;
        }, -100);


        $zfcServiceEvents = $sm->get('ZfcUser\Authentication\Adapter\AdapterChain')->getEventManager();
        $zfcServiceEvents->attach(
            'authenticate',
            function ($e) use ($sm) {
                $params = $e->getParams();
                $identity = $params['identity'];
//                $userService = $sm->get('application.service.user');
//                $userService->setLastLogin($sm, $identity);
            }
        );



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
       );

    }

    public function getViewHelperConfig()   {
        return array(
            'invokables' => array(
                'humanReadableBytes' => 'Application\View\Helper\HumanReadableBytes'
            )
        );
    }



}