<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */


class User {


  function get($id){
    $db = ezcDbInstance::get();

    $q = $db->createSelectQuery();
    $e = $q->expr;
    $q->select( '*' )->from( 'users' )
      ->where( $e->eq( 'user_id', $q->bindValue( $id ) ) );
    $stmt = $q->prepare();
    $stmt->execute();
    $rows = $stmt->fetchAll();
    return $rows[0];
  }


  function getAll(){
    $db = ezcDbInstance::get();

    $q = $db->createSelectQuery();
    $q->select( '*' )->from( 'users' )
      ->orderBy( 'fullname' );
    $stmt = $q->prepare();
    $stmt->execute();
    $rows = $stmt->fetchAll();
    return $rows;
  }


  function getPermissions($id){
    $db = ezcDbInstance::get();

    $q = $db->createSelectQuery();
    $e = $q->expr;
    $q->select( '*' )->from( 'groups' )->where( $e->eq( 'user_id', $q->bindValue( $id ) ) );

    $stmt = $q->prepare();
    $stmt->execute();

    $rows = $stmt->fetchAll();
    return $rows[0];
  }

  function getByCookie($cookie) {
    $db = ezcDbInstance::get();

    $q = $db->createSelectQuery();
    $e = $q->expr;
    $q->select( '*' )->from( 'users' )->where( $e->eq( 'cookie', $q->bindValue( $cookie ) ) );

    $stmt = $q->prepare();
    $stmt->execute();

    $rows = $stmt->fetchAll();
    return $rows[0];
  }


  function getByUsername($username) {
    $db = ezcDbInstance::get();

    $q = $db->createSelectQuery();
    $e = $q->expr;
    $q->select( '*' )->from( 'users' )->where( $e->eq( 'username', $q->bindValue( $username ) ) );

    $stmt = $q->prepare();
    $stmt->execute();

    $rows = $stmt->fetchAll();
    if (count($rows) == 0)
      return array();
    else
      return $rows[0];
  }


  function newCookie($id = 1) {
    $db = ezcDbInstance::get();

    $cookie = md5("sdkaghdig");

    $q = $db->createUpdateQuery();
    $e = $q->expr;
    $q->update( 'users' )
      ->set( 'cookie', $q->bindValue( $cookie ) )
      ->where( $e->eq( 'user_id', $q->bindValue( $id ) ) );
    $stmt = $q->prepare();
    $stmt->execute();

    return $cookie;
  }


  function delCookie($id = 1) {
    $db = ezcDbInstance::get();

    $cookie = "";

    $q = $db->createUpdateQuery();
    $e = $q->expr;
    $q->update( 'users' )
      ->set( 'cookie', $q->bindValue( $cookie ) )
      ->where( $e->eq( 'user_id', $q->bindValue( $id ) ) );
    $stmt = $q->prepare();
    $stmt->execute();

  }


  function isAuthed() {

    if (isset($_SESSION['wjukebox_auth']))
      $cookie = self::getByCookie($_SESSION['wjukebox_auth']);
    else
      return false;

    if (count($cookie) == 0)
      return false;
    else
      return true;

  }

}


?>