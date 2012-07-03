<?php


namespace WJB\Rest;

class Uri
{

    public function build($id, $class, $module = null)
    {

        if ($module == null)
            $module = \Zend_Controller_Front::getInstance()->getRequest()->getModuleName();

        $protocol = ((isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] == 'on')) ? 'https' : 'http';
        return sprintf("%s://%s/%s/%s/%s", $protocol, $_SERVER['HTTP_HOST'], $module, $class, $id);
    }


}
