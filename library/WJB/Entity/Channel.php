<?php

namespace WJB\Entity;

use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\ORM\Mapping as ORM;

/**
 * Channel
 *
 * @ORM\Table(name="channel")
 * @ORM\Entity(repositoryClass="WJB\Entity\Repository\ChannelRepository")
 */
class Channel
{
    /**
     * @var string $name
     *
     * @ORM\Column(name="name", type="string", length=32)
     */
    private $name;

    /**
     * @var string $backend
     *
     * @ORM\Column(name="backend", type="string", length=64)
     */
    private $backend;

    /**
     * @var string $backend_params
     *
     * @ORM\Column(name="backend_params", type="text")
     */
    private $backend_params;

    /**
     * @var integer $public
     *
     * @ORM\Column(name="public", type="integer")
     */
    private $public;

    /**
     * @var datetime $ping
     *
     * @ORM\Column(name="ping", type="datetime")
     */
    private $ping;

    /**
     * @var integer $active
     *
     * @ORM\Column(name="active", type="integer")
     */
    private $active;

    /**
     * @var integer $id
     *
     * @ORM\Column(name="id", type="integer")
     * @ORM\Id
     * @ORM\GeneratedValue(strategy="IDENTITY")
     */
    private $id;

    /**
     * @ORM\OneToMany(targetEntity="User", mappedBy="channel")
     * @ORM\OrderBy({"proofOfLife" = "DESC"})
     */
    private $users;

    /**
     * @param int $active
     */
    public function setActive($active)
    {
        $this->active = $active;
    }

    /**
     * @return int
     */
    public function getActive()
    {
        return $this->active;
    }

    /**
     * @param string $backend
     */
    public function setBackend($backend)
    {
        $this->backend = $backend;
    }

    /**
     * @return string
     */
    public function getBackend()
    {
        return $this->backend;
    }

    /**
     * @param string $backend_params
     */
    public function setBackendParams($backend_params)
    {
        $this->backend_params = $backend_params;
    }

    /**
     * @return string
     */
    public function getBackendParams()
    {
        return $this->backend_params;
    }

    /**
     * @return int
     */
    public function getId()
    {
        return $this->id;
    }

    /**
     * @param string $name
     */
    public function setName($name)
    {
        $this->name = $name;
    }

    /**
     * @return string
     */
    public function getName()
    {
        return $this->name;
    }

    /**
     * @param \WJB\Entity\datetime $ping
     */
    public function setPing($ping)
    {
        $this->ping = $ping;
    }

    /**
     * @return \WJB\Entity\datetime
     */
    public function getPing()
    {
        return $this->ping;
    }

    /**
     * @param int $public
     */
    public function setPublic($public)
    {
        $this->public = $public;
    }

    /**
     * @return int
     */
    public function getPublic()
    {
        return $this->public;
    }
}
