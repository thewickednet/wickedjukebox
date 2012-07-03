<?php

namespace WJB\Entity;

use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\ORM\Mapping as ORM;
use WJB\Rest\Uri as Uri;

/**
 * Album
 *
 * @ORM\Table(name="album")
 * @ORM\Entity(repositoryClass="WJB\Entity\Repository\AlbumRepository")
 */
class Album
{
    /**
     * @var string $name
     *
     * @ORM\Column(name="name", type="string", length=128)
     */
    private $name;

    /**
     * @var date $releaseDate
     *
     * @ORM\Column(name="release_date", type="date")
     */
    private $releaseDate;

    /**
     * @var string $type
     *
     * @ORM\Column(name="type", type="string", length=32)
     */
    private $type;

    /**
     * @var string $path
     *
     * @ORM\Column(name="path", type="string", length=255)
     */
    private $path;

    /**
     * @var integer $downloaded
     *
     * @ORM\Column(name="downloaded", type="integer")
     */
    private $downloaded;

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
     * @ORM\OneToMany(targetEntity="Song", mappedBy="album")
     * @ORM\OrderBy({"trackNo" = "ASC"})
     */
    private $songs;

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

    /**
     * @param int $downloaded
     */
    public function setDownloaded($downloaded)
    {
        $this->downloaded = $downloaded;
    }

    /**
     * @return int
     */
    public function getDownloaded()
    {
        return $this->downloaded;
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
     * @param string $path
     */
    public function setPath($path)
    {
        $this->path = $path;
    }

    /**
     * @return string
     */
    public function getPath()
    {
        return $this->path;
    }

    /**
     * @param \WJB\Entity\date $releaseDate
     */
    public function setReleaseDate($releaseDate)
    {
        $this->releaseDate = $releaseDate;
    }

    /**
     * @return \WJB\Entity\date
     */
    public function getReleaseDate()
    {
        return $this->releaseDate;
    }

    /**
     * @param string $type
     */
    public function setType($type)
    {
        $this->type = $type;
    }

    /**
     * @return string
     */
    public function getType()
    {
        return $this->type;
    }

    public function getArtist()
    {
        return $this->artist;
    }

    public function setSongs($songs)
    {
        $this->songs = $songs;
    }

    public function getSongs()
    {
        return $this->songs;
    }

    public function getPictureFile()
    {

        $filemasks = array(
            'folder.jpg',
            'Folder.jpg',
            'cover.jpg',
            'Cover.jpg',
            'Folder.png',
            'folder.png',
            'cover.png',
            'Cover.png',
            'folder.gif',
            'Folder.gif'
        );

        $path = $this->getPath();

        foreach ($filemasks as $filemask){
            $check = realpath($path . '/' . $filemask);
            $check = utf8_encode($check);
            if (file_exists($check))
                return $check;
        }
        return false;
    }

    public function toArray($deep = false)
    {
        $releaseDate = $this->getReleaseDate();

        if ($releaseDate != null)
            $releaseDate = $releaseDate->getTimestamp();

        $result = array(
            'id' => $this->getId(),
            'name' => $this->getName(),
            'release_date' => $releaseDate,
            'type' => $this->getType(),
            'downloads' => $this->getDownloaded(),
            'added' => $this->getAdded()->getTimestamp(),
            'uri' => Uri::build($this->getId(), 'album'),
            'class' => 'album'
        );
        if ($deep)
        {
            $result['artist'] = $this->getArtist()->toArray();
            $result['songs'] = array();
            foreach ($this->getSongs() as $song)
            {
                $result['songs'][] = $song->toArray();
            }
        }
        return $result;
    }

}
