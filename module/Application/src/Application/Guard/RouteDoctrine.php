<?php

namespace Application\Guard;

use BjyAuthorize\Guard\GuardInterface;
use BjyAuthorize\Provider\Rule\ProviderInterface as RuleProviderInterface;
use BjyAuthorize\Provider\Resource\ProviderInterface as ResourceProviderInterface;

use Zend\EventManager\EventManagerInterface;
use Zend\Mvc\MvcEvent;
use Zend\ServiceManager\ServiceLocatorInterface;

/**
 * Route Guard listener, allows checking of permissions
 * during {@see \Zend\Mvc\MvcEvent::EVENT_ROUTE}
 *
 * @author Ben Youngblood <bx.youngblood@gmail.com>
 */
class RouteDoctrine implements GuardInterface, RuleProviderInterface, ResourceProviderInterface
{
    /**
     * Marker for invalid route errors
     */
    const ERROR = 'error-unauthorized-route';

    /**
     * @var ServiceLocatorInterface
     */
    protected $serviceLocator;

    /**
     * @var array[]
     */
    protected $rules = array();

    /**
     * @var \Zend\Stdlib\CallbackHandler[]
     */
    protected $listeners = array();

    /**
     * @param array                   $rules
     * @param ServiceLocatorInterface $serviceLocator
     */
    public function __construct(array $rules, ServiceLocatorInterface $serviceLocator)
    {

        $this->serviceLocator = $serviceLocator;

        /** @var \Zend\Cache\Storage\Adapter\Memcached $cache */
        $cache = $this->serviceLocator->get('application.cache');

        $cacheKey = "cache.application.guard.route_doctrine";

        $rules = $cache->getItem($cacheKey, $success);

        if (!$success)
        {

            $em = $this->serviceLocator->get('zfcuser_doctrine_em');

            $repos = $em->getRepository('Application\Entity\RouteGuard');

            $rules = array();

            foreach ($repos->findAll() as $rule) {

                $roles = array();
                foreach ($rule->getRoles() as $role)
                {
                    $roles[] = $role->getRoleId();
                }
                if (count($roles) > 0)
                    $rules['route/' . $rule->getRoute()] = $roles;
            }
            $cache->setItem($cacheKey, $rules);
        }
        $this->rules = $rules;
        return;
    }

    /**
     * {@inheritDoc}
     */
    public function attach(EventManagerInterface $events)
    {
        $this->listeners[] = $events->attach(MvcEvent::EVENT_ROUTE, array($this, 'onRoute'), -1000);
    }

    /**
     * {@inheritDoc}
     */
    public function detach(EventManagerInterface $events)
    {
        foreach ($this->listeners as $index => $listener) {
            if ($events->detach($listener)) {
                unset($this->listeners[$index]);
            }
        }
    }

    /**
     * {@inheritDoc}
     */
    public function getResources()
    {
        $resources = array();

        foreach (array_keys($this->rules) as $resource) {
            $resources[] = $resource;
        }

        return $resources;
    }

    /**
     * {@inheritDoc}
     */
    public function getRules()
    {
        $rules = array();

        foreach ($this->rules as $resource => $roles) {
            $rules[] = array($roles, $resource);
        }

        return array('allow' => $rules);
    }

    /**
     * Event callback to be triggered on dispatch, causes application error triggering
     * in case of failed authorization check
     *
     * @param MvcEvent $event
     *
     * @return void
     */
    public function onRoute(MvcEvent $event)
    {
        $service    = $this->serviceLocator->get('BjyAuthorize\Service\Authorize');
        $match      = $event->getRouteMatch();
        $routeName  = $match->getMatchedRouteName();

        if ($service->isAllowed('route/' . $routeName)) {
            return;
        }

        $event->setError(static::ERROR);
        $event->setParam('route', $routeName);
        $event->setParam('identity', $service->getIdentity());

        /* @var $app \Zend\Mvc\Application */
        $app = $event->getTarget();

        $app->getEventManager()->trigger(MvcEvent::EVENT_DISPATCH_ERROR, $event);
    }
}
