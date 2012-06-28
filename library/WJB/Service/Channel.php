<?php

namespace WJB\Service;


class Channel extends \WJB\Service {

    private $_channelRepo;

    public function __construct()
    {
        parent::__construct();
        $this->_channelRepo = $this->getRepo('\WJB\Entity\Channel');
    }


    public function getAll()
    {
        return $this->_channelRepo->findAll();
    }

    public function getById($id)
    {
        return $this->_channelRepo->find($id);
    }




}