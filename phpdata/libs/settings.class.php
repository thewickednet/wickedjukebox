<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */


class Setting {


  function get($name){
    $db = ezcDbInstance::get();

    $q = $db->createSelectQuery();
    $e = $q->expr;
    $q->select( '*' )->from( 'settings' )
      ->where( $e->eq( 'name', $q->bindValue( $name ) ) );
    $stmt = $q->prepare();
    $stmt->execute();
    $rows = $stmt->fetchAll();
    return $rows[0];
  }



}


?>