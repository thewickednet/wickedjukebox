<?php


namespace WJB\Rest;

class Uri
{

    public function build($id, $class)
    {

        $front = \Zend_Controller_Front::getInstance();

        $config = \Zend_Registry::get('config')->toArray();

        $rest_config = $config['wjb']['rest'];

        $module = $rest_config['module'];
        $http_host = $rest_config['http_host'];

        return sprintf("%s/%s/%s/%d", $http_host, $module, $class, $id);

        //$protocol = ((isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] == 'on')) ? 'https' : 'http';
        //return sprintf("%s://%s/%s/%s/%s", $protocol, $_SERVER['HTTP_HOST'], $module, $class, $id);
    }


}
