<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */

  $smarty->debugging = false;

  if ($_GET['mode'] == 'logout') {

    unset($_SESSION['wjukebox_auth']);
    User::delCookie($userinfo['auth_id']);
    $base_template = 'reload.tpl';

  } else {

    $base_template = 'login.tpl';

    if (!User::isAuthed()) {

    $username = $_GET['username'];
    $password = $_GET['password'];

      if (!empty($username) || !empty($password)) {
        $auth_user = User::getByUsername($username);
        if (count($auth_user) == 0) {
          $smarty->assign("AUTH_ERROR", "username does not exist!");
        } else {
          if ($auth_user['password'] != $password) {
            $smarty->assign("AUTH_ERROR", "incorrect password");
            $smarty->assign("AUTH_USER", $username);
          } else {
            $cookie = User::newCookie($auth_user['user_id']);
            setcookie("wjukebox_auth", $cookie);
            $_SESSION['wjukebox_auth'] = $cookie;
            $userinfo = $auth_user;
            $base_template = 'reload.tpl';
          }

        }

      } else {
        $smarty->assign("AUTH_ERROR", "Please specify username and password!");
      }

    }
  }

?>