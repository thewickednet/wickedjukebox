<?php

namespace WJB\Entity;

use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\ORM\Mapping as ORM;

/**
 * User
 *
 * @ORM\Table(name="users")
 * @ORM\Entity(repositoryClass="WJB\Entity\Repository\UserRepository")
 */
class User
{
    /**
     * @var string $username
     *
     * @ORM\Column(name="username", type="string", length=32)
     */
    private $username;

    /**
     * @var string $password
     *
     * @ORM\Column(name="password", type="string", length=32)
     */
    private $password;

    /**
     * @var string $cookie
     *
     * @ORM\Column(name="cookie", type="string", length=32)
     */
    private $cookie;

    /**
     * @var string $fullname
     *
     * @ORM\Column(name="fullname", type="string", length=64)
     */
    private $fullname;

    /**
     * @var string $name
     *
     * @ORM\Column(name="email", type="string", length=128)
     */
    private $email;

    /**
     * @var integer $credits
     *
     * @ORM\Column(name="credits", type="integer")
     */
    private $credits;

    /**
     * @var integer $downloads
     *
     * @ORM\Column(name="downloads", type="integer")
     */
    private $downloads;

    /**
     * @var integer $votes
     *
     * @ORM\Column(name="votes", type="integer")
     */
    private $votes;

    /**
     * @var integer $skips
     *
     * @ORM\Column(name="skips", type="integer")
     */
    private $skips;

    /**
     * @var integer $selects
     *
     * @ORM\Column(name="selects", type="integer")
     */
    private $selects;

    /**
     * @var integer $channelId
     *
     * @ORM\Column(name="channel_id", type="integer")
     */
    private $channelId;

    /**
     * @var string $added
     *
     * @ORM\Column(name="added", type="datetime")
     */
    private $added;

    /**
     * @var string $proofOfLife
     *
     * @ORM\Column(name="proof_of_life", type="datetime")
     */
    private $proofOfLife;

    /**
     * @var string $proofOfListening
     *
     * @ORM\Column(name="proof_of_listening", type="datetime")
     */
    private $proofOfListening;

    /**
     * @var string $picture
     *
     * @ORM\Column(name="picture", type="string")
     */
    private $picture;

    /**
     * @var string $proofOfListening
     *
     * @ORM\Column(name="IP", type="string")
     */
    private $IP;

    /**
     * @ORM\ManyToOne(targetEntity="Group")
     * @ORM\JoinColumn(name="group_id", referencedColumnName="id")
     */
    private $group;

    /**
     * @ORM\ManyToOne(targetEntity="Channel")
     * @ORM\JoinColumn(name="channel_id", referencedColumnName="id")
     */
    private $channel;

    /**
     * @var integer $id
     *
     * @ORM\Column(name="id", type="integer")
     * @ORM\Id
     * @ORM\GeneratedValue(strategy="IDENTITY")
     */
    private $id;


    /**
     * @param string $IP
     */
    public function setIP($IP)
    {
        $this->IP = $IP;
    }

    /**
     * @return string
     */
    public function getIP()
    {
        return $this->IP;
    }

    /**
     * @param string $added
     */
    public function setAdded($added)
    {
        $this->added = $added;
    }

    /**
     * @return string
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
     * @param string $cookie
     */
    public function setCookie($cookie)
    {
        $this->cookie = $cookie;
    }

    /**
     * @return string
     */
    public function getCookie()
    {
        return $this->cookie;
    }

    /**
     * @param int $credits
     */
    public function setCredits($credits)
    {
        $this->credits = $credits;
    }

    /**
     * @return int
     */
    public function getCredits()
    {
        return $this->credits;
    }

    /**
     * @param int $downloads
     */
    public function setDownloads($downloads)
    {
        $this->downloads = $downloads;
    }

    /**
     * @return int
     */
    public function getDownloads()
    {
        return $this->downloads;
    }

    /**
     * @param string $email
     */
    public function setEmail($email)
    {
        $this->email = $email;
    }

    /**
     * @return string
     */
    public function getEmail()
    {
        return $this->email;
    }

    /**
     * @param string $fullname
     */
    public function setFullname($fullname)
    {
        $this->fullname = $fullname;
    }

    /**
     * @return string
     */
    public function getFullname()
    {
        return $this->fullname;
    }

    public function setGroup($group)
    {
        $this->group = $group;
    }

    public function getGroup()
    {
        return $this->group;
    }

    /**
     * @return int
     */
    public function getId()
    {
        return $this->id;
    }

    /**
     * @param string $password
     */
    public function setPassword($password)
    {
        $this->password = $password;
    }

    /**
     * @return string
     */
    public function getPassword()
    {
        return $this->password;
    }

    /**
     * @param string $picture
     */
    public function setPicture($picture)
    {
        $this->picture = $picture;
    }

    /**
     * @return string
     */
    public function getPicture()
    {
        return $this->picture;
    }

    /**
     * @param string $proofOfLife
     */
    public function setProofOfLife($proofOfLife)
    {
        $this->proofOfLife = $proofOfLife;
    }

    /**
     * @return string
     */
    public function getProofOfLife()
    {
        return $this->proofOfLife;
    }

    /**
     * @param string $proofOfListening
     */
    public function setProofOfListening($proofOfListening)
    {
        $this->proofOfListening = $proofOfListening;
    }

    /**
     * @return string
     */
    public function getProofOfListening()
    {
        return $this->proofOfListening;
    }

    /**
     * @param int $selects
     */
    public function setSelects($selects)
    {
        $this->selects = $selects;
    }

    /**
     * @return int
     */
    public function getSelects()
    {
        return $this->selects;
    }

    /**
     * @param int $skips
     */
    public function setSkips($skips)
    {
        $this->skips = $skips;
    }

    /**
     * @return int
     */
    public function getSkips()
    {
        return $this->skips;
    }

    /**
     * @param string $username
     */
    public function setUsername($username)
    {
        $this->username = $username;
    }

    /**
     * @return string
     */
    public function getUsername()
    {
        return $this->username;
    }

    /**
     * @param int $votes
     */
    public function setVotes($votes)
    {
        $this->votes = $votes;
    }

    /**
     * @return int
     */
    public function getVotes()
    {
        return $this->votes;
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

    public function toArray()
    {
        return array(
            'id' => $this->getId(),
            'channel_id' => $this->getChannelId(),
            'username' => $this->getUsername(),
            'fullname' => $this->getFullname(),
            'email' => $this->getEmail(),
            'selects' => $this->getSelects(),
            'skips' => $this->getSkips(),
            'downloads' => $this->getDownloads(),
            'votes' => $this->getVotes(),
            'group' => $this->getGroup()->toArray(),
            'credits' => $this->getCredits(),
            'proof_of_life' => $this->getProofOfLife()->getTimestamp(),
            'proof_of_listening' => $this->getProofOfListening()->getTimestamp(),
            'ip' => $this->getIP(),
            'added' => $this->getAdded()->getTimestamp(),
            'picture' => $this->getPicture()
        );
    }


}
