<?php

namespace WJB\Entity;

use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\ORM\Mapping as ORM;

/**
 * Group
 *
 * @ORM\Table(name="groups")
 * @ORM\Entity(repositoryClass="WJB\Entity\Repository\GroupRepository")
 */
class Group
{
    /**
     * @var string $title
     *
     * @ORM\Column(name="title", type="string", length=32)
     */
    private $title;

    /**
     * @var integer $admin
     *
     * @ORM\Column(name="admin", type="integer")
     */
    private $admin;

    /**
     * @var integer $nocredits
     *
     * @ORM\Column(name="nocredits", type="integer")
     */
    private $nocredits;

    /**
     * @var integer $queueSkip
     *
     * @ORM\Column(name="queue_skip", type="integer")
     */
    private $queueSkip;

    /**
     * @var integer $queueRemove
     *
     * @ORM\Column(name="queue_remove", type="integer")
     */
    private $queueRemove;

    /**
     * @var integer $queueAdd
     *
     * @ORM\Column(name="queue_add", type="integer")
     */
    private $queueAdd;

    /**
     * @var integer $id
     *
     * @ORM\Column(name="id", type="integer")
     * @ORM\Id
     * @ORM\GeneratedValue(strategy="IDENTITY")
     */
    private $id;

    /**
     * @ORM\OneToMany(targetEntity="User", mappedBy="group")
     * @ORM\OrderBy({"added" = "ASC"})
     */
    private $users;


    /**
     * @param int $admin
     */
    public function setAdmin($admin)
    {
        $this->admin = $admin;
    }

    /**
     * @return int
     */
    public function getAdmin()
    {
        return $this->admin;
    }

    /**
     * @param int $id
     */
    public function setId($id)
    {
        $this->id = $id;
    }

    /**
     * @return int
     */
    public function getId()
    {
        return $this->id;
    }

    /**
     * @param int $nocredits
     */
    public function setNocredits($nocredits)
    {
        $this->nocredits = $nocredits;
    }

    /**
     * @return int
     */
    public function getNocredits()
    {
        return $this->nocredits;
    }

    /**
     * @param int $queueAdd
     */
    public function setQueueAdd($queueAdd)
    {
        $this->queueAdd = $queueAdd;
    }

    /**
     * @return int
     */
    public function getQueueAdd()
    {
        return $this->queueAdd;
    }

    /**
     * @param int $queueRemove
     */
    public function setQueueRemove($queueRemove)
    {
        $this->queueRemove = $queueRemove;
    }

    /**
     * @return int
     */
    public function getQueueRemove()
    {
        return $this->queueRemove;
    }

    /**
     * @param int $queueSkip
     */
    public function setQueueSkip($queueSkip)
    {
        $this->queueSkip = $queueSkip;
    }

    /**
     * @return int
     */
    public function getQueueSkip()
    {
        return $this->queueSkip;
    }

    /**
     * @param string $title
     */
    public function setTitle($title)
    {
        $this->title = $title;
    }

    /**
     * @return string
     */
    public function getTitle()
    {
        return $this->title;
    }

    public function setUsers($users)
    {
        $this->users = $users;
    }

    public function getUsers()
    {
        return $this->users;
    }

    public function toArray($deep = false)
    {
        return array(
            'title' => $this->getTitle(),
            'queue_add' => $this->getQueueAdd(),
            'queue_skip' => $this->getQueueSkip(),
            'queue_remove' => $this->getQueueRemove(),
            'nocredits' => $this->getNocredits(),
            'admin' => $this->getAdmin()
        );
    }

}
