<?php
/**
 * BjyAuthorize Module (https://github.com/bjyoungblood/BjyAuthorize)
 *
 * @link https://github.com/bjyoungblood/BjyAuthorize for the canonical source repository
 * @license http://framework.zend.com/license/new-bsd New BSD License
 */

namespace Application\Entity;

use BjyAuthorize\Acl\HierarchicalRoleInterface;
use Doctrine\ORM\Mapping as ORM;
use Doctrine\Common\Collections\ArrayCollection;

/**
 * An example entity that represents a role.
 *
 * @ORM\Entity
 * @ORM\Table(name="role")
 *
 * @author Tom Oram <tom@scl.co.uk>
 */
class Role implements HierarchicalRoleInterface
{
    /**
     * @var int
     * @ORM\Id
     * @ORM\Column(type="integer")
     * @ORM\GeneratedValue(strategy="AUTO")
     */
    protected $id;

    /**
     * @var string
     * @ORM\Column(type="string", length=255, unique=true, nullable=true)
     */
    protected $roleId;

    /**
     * @ORM\OneToMany(targetEntity="Role", mappedBy="parent")
     */
    private $children;

    /**
     * @var Role
     * @ORM\ManyToOne(targetEntity="Role", inversedBy="children")
     * @ORM\JoinColumn(name="parent_id", referencedColumnName="id")
     */
    protected $parent;

    /**
     * @var string
     * @ORM\Column(type="string", length=255, unique=false, nullable=true)
     */
    protected $description;

    /**
     * @var \Doctrine\Common\Collections\Collection
     * @ORM\ManyToMany(targetEntity="RouteGuard")
     * @ORM\JoinTable(name="guard_route_role",
     *      joinColumns={@ORM\JoinColumn(name="role_id", referencedColumnName="id")},
     *      inverseJoinColumns={@ORM\JoinColumn(name="guard_id", referencedColumnName="id")}
     * )
     */
    protected $routeGuards;

    /**
     * @var \Doctrine\Common\Collections\Collection
     * @ORM\ManyToMany(targetEntity="User", mappedBy="roles")
     */
    protected $users;

    /**
     * Initialies the roles variable.
     */
    public function __construct()
    {
        $this->routeGuards = new ArrayCollection();
        $this->children = new ArrayCollection();
    }

    /**
     * Get the id.
     *
     * @return int
     */
    public function getId()
    {
        return $this->id;
    }

    /**
     * Set the id.
     *
     * @param int $id
     *
     * @return void
     */
    public function setId($id)
    {
        $this->id = (int)$id;
    }

    /**
     * Get the role id.
     *
     * @return string
     */
    public function getRoleId()
    {
        return $this->roleId;
    }

    /**
     * Set the role id.
     *
     * @param string $roleId
     *
     * @return void
     */
    public function setRoleId($roleId)
    {
        $this->roleId = (string) $roleId;
    }

    /**
     * Get the parent role
     *
     * @return Role
     */
    public function getParent()
    {
        return $this->parent;
    }

    /**
     * Set the parent role.
     *
     * @param Role $role
     *
     * @return void
     */
    public function setParent(Role $parent)
    {
        $this->parent = $parent;
    }

    /**
     * Get the description.
     *
     * @return string
     */
    public function getDescription()
    {
        return $this->description;
    }

    /**
     * Set the description.
     *
     * @param string $description
     *
     * @return void
     */
    public function setDescription($description)
    {
        $this->description = (string) $description;
    }

    /**
     * Remove all the RouteGuards
     *
     * @return void
     */
    public function removeAllRouteGuards()
    {
        $this->routeGuards = array();
    }

    /**
     * Add a routeguard to the role.
     *
     * @param RouteGuard $routeGuard
     *
     * @return void
     */
    public function addRouteGuard($routeGuard)
    {
        $this->routeGuards[] = $routeGuard;
    }

    /**
     * Get routeGuards.
     *
     * @return array
     */
    public function getRouteGuards()
    {
        return $this->routeGuards->getValues();
    }

}
