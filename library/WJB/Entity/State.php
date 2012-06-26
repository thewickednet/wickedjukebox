<?php

namespace WJB\Entity;

use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\ORM\Mapping as ORM;

/**
 * State
 *
 * @ORM\Table(name="state")
 * @ORM\Entity(repositoryClass="WJB\Entity\Repository\ChannelRepository")
 */
class State
{
    /**
     * @var integer $channelId
     *
     * @ORM\Column(name="channel_id", type="integer")
     * @ORM\Id
     */
    private $channelId;

    /**
     * @var integer $state
     *
     * @ORM\Column(name="state", type="string", length=64)
     * @ORM\Id
     */
    private $state;

    /**
     * @var string $value
     *
     * @ORM\Column(name="value", type="string", length=255)
     */
    private $value;

    /**
     * @ORM\ManyToOne(targetEntity="Channel")
     * @ORM\JoinColumn(name="channel_id", referencedColumnName="id")
     */
    private $channel;


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
    public function getState()
    {
        return $this->state;
    }

    /**
     * @param string $value
     */
    public function setValue($value)
    {
        $this->value = $value;
    }

    /**
     * @return string
     */
    public function getValue()
    {
        return $this->value;
    }

    public function getChannel()
    {
        return $this->channel;
    }

}
