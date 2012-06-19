<?php

namespace WJB\Entity;

use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\ORM\Mapping as ORM;

/**
 * Queue
 *
 * @ORM\Table(name="queue")
 * @ORM\Entity(repositoryClass="WJB\Entity\Repository\QueueRepository")
 */
class Queue
{
    /**
     * @var integer $songId
     *
     * @ORM\Column(name="song_id", type="integer")
     */
    private $songId;

    /**
     * @var integer $user_id
     *
     * @ORM\Column(name="user_id", type="integer")
     */
    private $userId;

    /**
     * @var integer $channelId
     *
     * @ORM\Column(name="channel_id", type="integer")
     */
    private $channelId;

    /**
     * @var integer $position
     *
     * @ORM\Column(name="position", type="integer")
     */
    private $position;

    /**
     * @var datetime $added
     *
     * @ORM\Column(name="added", type="datetime")
     */
    private $added;

    /**
     * @var integer $id
     *
     * @ORM\Column(name="id", type="integer")
     * @ORM\Id
     * @ORM\GeneratedValue(strategy="IDENTITY")
     */
    private $id;

    /**
     * @ORM\ManyToOne(targetEntity="Song")
     * @ORM\JoinColumn(name="song_id", referencedColumnName="id")
     */
    private $song;

    /**
     * @ORM\ManyToOne(targetEntity="User")
     * @ORM\JoinColumn(name="user_id", referencedColumnName="id")
     */
    private $user;

    /**
     * @ORM\ManyToOne(targetEntity="Channel")
     * @ORM\JoinColumn(name="channel_id", referencedColumnName="id")
     */
    private $channel;


    /**
     * @param \WJB\Entity\datetime $added
     */
    public function setAdded($added)
    {
        $this->added = $added;
    }

    /**
     * @return \WJB\Entity\datetime
     */
    public function getAdded()
    {
        return $this->added;
    }

    public function setChannel($channel)
    {
        $this->channel = $channel;
    }

    public function getChannel()
    {
        return $this->channel;
    }

    /**
     * @param int $channelId
     */
    public function setChannelId($channelId)
    {
        $this->channelId = $channelId;
    }

    /**
     * @return int
     */
    public function getChannelId()
    {
        return $this->channelId;
    }

    /**
     * @return int
     */
    public function getId()
    {
        return $this->id;
    }

    /**
     * @param int $position
     */
    public function setPosition($position)
    {
        $this->position = $position;
    }

    /**
     * @return int
     */
    public function getPosition()
    {
        return $this->position;
    }

    public function setSong($song)
    {
        $this->song = $song;
    }

    public function getSong()
    {
        return $this->song;
    }

    /**
     * @param int $songId
     */
    public function setSongId($songId)
    {
        $this->songId = $songId;
    }

    /**
     * @return int
     */
    public function getSongId()
    {
        return $this->songId;
    }

    public function setUser($user)
    {
        $this->user = $user;
    }

    public function getUser()
    {
        return $this->user;
    }

    /**
     * @param int $userId
     */
    public function setUserId($userId)
    {
        $this->userId = $userId;
    }

    /**
     * @return int
     */
    public function getUserId()
    {
        return $this->userId;
    }
}
