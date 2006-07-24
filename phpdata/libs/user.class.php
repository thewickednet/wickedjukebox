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
    $q->select( '*' )->from( 'groups' );

    $stmt = $q->prepare();
    $stmt->execute();

  }

}


?>