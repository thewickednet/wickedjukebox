<?php


class WJB_Form_Login extends Zend_Form
{

    public function init()
    {

        $this->setMethod('post')
            ->setAction($this->getView()->url(array(
            'module' => 'auth',
            'controller' => 'login',
            'action' => 'index')))
            ->setAttrib('class', 'box')
            ->setName('Login');

        # Username
        $username = new Zend_Form_Element_Text('username');
        $username->setLabel('Username')
            ->setRequired(TRUE)
            ->addFilter('StripTags')
            ->addFilter('StringTrim')
            ->addFilter('StringToLower')
            ->addValidator('NotEmpty');

        # Password
        $password = new Zend_Form_Element_Password('password');
        $password->setLabel('Password')
            ->setRequired(TRUE)
            ->addFilter('StripTags')
            ->addFilter('StringTrim')
            ->addValidator('NotEmpty');

        $hash = new Zend_Form_Element_Hash('csrf', array('salt' => 'unique'));
        $hash->setTimeout(300)
            ->addErrorMessage('Form timed out. Please reload the page & try again');

        # Submit
        $submit = new Zend_Form_Element_Submit('Login');

        # Create
        $this->addElements(array($username, $password, $submit));
    }
}

