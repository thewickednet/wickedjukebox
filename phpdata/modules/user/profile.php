<?

    $user = User::getUser($_GET['id']);

    $smarty->assign("USER", $user);
    
    $form = new Zend_Form;

    $username = new Zend_Form_Element_Text('username');
    $username->setRequired(true);
    $form->addElement($username);

    $email = new Zend_Form_Element_Text('email');
    $email->setRequired(true);
    $form->addElement($email);

    $form->setElementFilters(array('StringTrim'));

    $body_template = 'user/profile.tpl';

?>