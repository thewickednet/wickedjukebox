<?php


  if ($_GET['mode'] == 'logout') {

    unset($_SESSION['wjukebox_auth']);
    Auth::delCookie($userinfo['auth_id']);
    $core->template = 'reload.tpl';
    $smarty->assign("RELOAD_MESSAGE", "LOGOUT_SUCCESS");
    header("Location: /");
    exit();

  } else {

    $core->template = 'notloggedin.tpl';

    if ($core->user_id == -1) {

    $username = trim($_POST['username']);
    $password = trim($_POST['password']);

      if (!empty($username) || !empty($password)) {
        $auth_user = Auth::getByUsername($username);
        if (count($auth_user) == 0) {
          $smarty->assign("AUTH_ERROR", "username does not exist!");
        } else {
          if (trim($auth_user['password']) != md5($password)) {
            $smarty->assign("AUTH_ERROR", "incorrect password");
            $smarty->assign("AUTH_USER", $username);
          } else {
            $cookie = Auth::newCookie($auth_user['id']);
            setcookie("wjukebox_auth", $cookie);
            $_SESSION['wjukebox_auth'] = $cookie;
            header("Location: /");
            exit();
          }

        }

      } else {
        $smarty->assign("AUTH_ERROR", "Please specify username and password!");
      }

    }
  }

?>