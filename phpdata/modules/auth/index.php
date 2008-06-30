<?php


  if ($_GET['mode'] == 'logout') {

    unset($_SESSION['wjukebox_auth']);
    Auth::delCookie($userinfo['auth_id']);
    $core->template = 'reload.tpl';
    $smarty->assign("RELOAD_MESSAGE", "LOGOUT_SUCCESS");
    header("Location: /");
    exit();

  } else {

    $core->template = 'login.tpl';

    if ($core->user_id == -1) {

    $username = trim($_GET['username']);
    $password = trim($_GET['password']);

      if (!empty($username) || !empty($password)) {
        $auth_user = Auth::getByUsername($username);
        if (count($auth_user) == 0) {
          $smarty->assign("AUTH_ERROR", "username does not exist!");
        } else {
          if (trim($auth_user['password']) != $password) {
            $smarty->assign("AUTH_ERROR", "incorrect password");
            $smarty->assign("AUTH_USER", $username);
          } else {
            $cookie = Auth::newCookie($auth_user['id']);
            setcookie("wjukebox_auth", $cookie);
            $_SESSION['wjukebox_auth'] = $cookie;
            $core->userinfo = $auth_user;
            $core->template = 'reload.tpl';
            $smarty->assign("RELOAD_MESSAGE", "AUTH_SUCCESS: $cookie");
          }

        }

      } else {
        $smarty->assign("AUTH_ERROR", "Please specify username and password!");
      }

    }
  }

?>