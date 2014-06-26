<?php

namespace Jukebox\Entity;

use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\ORM\Mapping as ORM;

/**
 * Country
 *
 * @ORM\Table(name="country")
 * @ORM\Entity
 */
class Country
{
    /**
     * @var string $countryCode
     *
     * @ORM\Column(name="country_code", type="string", length=16)
     * @ORM\Id
     */
    private $countryCode;

    /**
     * @var string $countryName
     *
     * @ORM\Column(name="country_name", type="string", length=100)
     */
    private $countryName;


    /**
     * @return string
     */
    public function getId()
    {
        return $this->countryCode;
    }

    /**
     * @return string
     */
    public function getCountryCode()
    {
        return $this->countryCode;
    }

    /**
     * @param string $countryName
     */
    public function setCountryName($countryName)
    {
        $this->countryName = $countryName;
    }

    /**
     * @return string
     */
    public function getCountryName()
    {
        return $this->countryName;
    }
}