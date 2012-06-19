<?php

namespace WJB\Entity;

use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\ORM\Mapping as ORM;

/**
 * Song
 *
 * @ORM\Table(name="song")
 * @ORM\Entity(repositoryClass="WJB\Entity\Repository\SongRepository")
 */
class Song
{
    /**
     * @var string $title
     *
     * @ORM\Column(name="title", type="string", length=128)
     */
    private $title;

    /**
     * @var string $localpath
     *
     * @ORM\Column(name="localpath", type="string", length=255)
     */
    private $localpath;

    /**
     * @var string $trackNo
     *
     * @ORM\Column(name="track_no", type="integer")
     */
    private $trackNo;

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
     * @ORM\ManyToOne(targetEntity="Artist")
     * @ORM\JoinColumn(name="artist_id", referencedColumnName="id")
     */
    private $artist;


    /**
     * @ORM\ManyToOne(targetEntity="Album")
     * @ORM\JoinColumn(name="album_id", referencedColumnName="id")
     */
    private $album;


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

    public function setAlbum($album)
    {
        $this->album = $album;
    }

    public function getAlbum()
    {
        return $this->album;
    }

    public function setArtist($artist)
    {
        $this->artist = $artist;
    }

    public function getArtist()
    {
        return $this->artist;
    }

    /**
     * @return int
     */
    public function getId()
    {
        return $this->id;
    }

    /**
     * @param string $localpath
     */
    public function setLocalpath($localpath)
    {
        $this->localpath = $localpath;
    }

    /**
     * @return string
     */
    public function getLocalpath()
    {
        return $this->localpath;
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

    /**
     * @param string $trackNo
     */
    public function setTrackNo($trackNo)
    {
        $this->trackNo = $trackNo;
    }

    /**
     * @return string
     */
    public function getTrackNo()
    {
        return $this->trackNo;
    }
}
