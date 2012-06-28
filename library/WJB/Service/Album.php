<?php

namespace WJB\Service;


class Album extends \WJB\Service {


    public function __construct()
    {
        parent::__construct();
        $this->setDefaultRepo('\WJB\Entity\Album');
    }


}
