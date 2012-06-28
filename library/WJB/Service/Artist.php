<?php

namespace WJB\Service;


class Artist extends \WJB\Service {


    public function __construct()
    {
        parent::__construct();
        $this->setDefaultRepo('\WJB\Entity\Artist');
    }

}
