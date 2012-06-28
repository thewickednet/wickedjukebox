<?php

namespace WJB\Service;


class Song extends \WJB\Service {


    public function __construct()
    {
        parent::__construct();
        $this->setDefaultRepo('\WJB\Entity\Song');
    }

}
