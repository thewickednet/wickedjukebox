<?php

namespace WJB\Service;


class Channel extends \WJB\Service {


    public function __construct()
    {
        parent::__construct();
        $this->setDefaultRepo('\WJB\Entity\Channel');
    }


}
