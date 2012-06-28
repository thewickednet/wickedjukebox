<?php

namespace WJB\Service;


class Channel extends \WJB\Service {

    private $_channelRepo;

    public function __construct()
    {
        parent::__construct();
        $this->setDefaultRepo('\WJB\Entity\Channel');
    }



}