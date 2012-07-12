<?php

namespace WJB\Entity;

use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\ORM\Mapping as ORM;
use WJB\Rest\Uri as Uri;

/**
 * Artist
 *
 * @ORM\Table(name="artist")
 * @ORM\Entity(repositoryClass="WJB\Entity\Repository\ArtistRepository")
 */
class Artist
{
    /**
     * @var string $name
     *
     * @ORM\Column(name="name", type="string", length=128)
     */
    private $name;

    /**
     * @var datetime $added
     *
     * @ORM\Column(name="added", type="datetime")
     */
    private $added;

    /**
     * @var string $countryCode
     *
     * @ORM\Column(name="country", type="string", length=16)
     */
    private $countryCode;

    /**
     * @var string $bio
     *
     * @ORM\Column(name="bio", type="text")
     */
    private $bio;

    /**
     * @var string $summary
     *
     * @ORM\Column(name="summary", type="text")
     */
    private $summary;

    /**
     * @ORM\ManyToOne(targetEntity="Country")
     * @ORM\JoinColumn(name="country", referencedColumnName="country_code")
     */
    private $country;

    /**
     * @var integer $id
     *
     * @ORM\Column(name="id", type="integer")
     * @ORM\Id
     * @ORM\GeneratedValue(strategy="IDENTITY")
     */
    private $id;


    /**
     * @ORM\OneToMany(targetEntity="Album", mappedBy="artist")
     * @ORM\OrderBy({"releaseDate" = "DESC"})
     */
    private $albums;

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
     * @param \WJB\Entity\date $added
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
     * @return int
     */
    public function getId()
    {
        return $this->id;
    }

    public function getAlbums()
    {
        return $this->albums;
    }



    public function getPictureFile()
    {

        $log = Zend_Registry::get('log');

        $path = '';
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

        $albums = $this->getAlbums();

        $sourceAlbum = null;

        foreach ($albums as $album)
        {
            if ($album->getType() == 'album')
            {
                $path = sprintf("%s/../", $album->getPath());
                $path = realpath($path);
            }
        }

        foreach ($filemasks as $filemask){
            $check = realpath($path . '/' . $filemask);
            $check = utf8_encode($check);
            if (file_exists($check))
            {
                $log->info(sprintf("testing path: %s - result: %s", $check, 'FOUND'));
                return $check;
            }
            else
            {
                $log->info(sprintf("testing path: %s - result: %s", $check, 'NOT FOUND'));
            }
        }
        return false;
    }

    public function toArray($deep = false)
    {
        $result = array(
            'id' => $this->getId(),
            'name' => $this->getName(),
            'added' => $this->getAdded()->getTimestamp(),
            'uri' => Uri::build($this->getId(), 'artist'),
            'class' => 'artist'
        );
        if ($deep)
        {
            $result['albums'] = array();
            foreach ($this->getAlbums() as $album)
            {
                $result['albums'][] = $album->toArray();
            }
        }
        return $result;
    }

    /**
     * @param string $summary
     */
    public function setSummary($summary)
    {
        $this->summary = $summary;
    }

    /**
     * @return string
     */
    public function getSummary()
    {
        return $this->summary;
    }

    /**
     * @param string $bio
     */
    public function setBio($bio)
    {
        $this->bio = $bio;
    }

    /**
     * @return string
     */
    public function getBio()
    {
        return $this->bio;
    }

    public function setCountry($country)
    {
        $this->country = $country;
    }

    public function getCountry()
    {
        return $this->country;
    }

    /**
     * @param string $countryCode
     */
    public function setCountryCode($countryCode)
    {
        $this->countryCode = $countryCode;
    }

    /**
     * @return string
     */
    public function getCountryCode()
    {
        return $this->countryCode;
    }

}
