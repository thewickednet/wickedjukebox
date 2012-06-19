<?php

namespace WJB\Entity;

use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\ORM\Mapping as ORM;

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


}
