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
      ->where( $e->eq( 'param', $q->bindValue( $name ) ) );
    $stmt = $q->prepare();
    $stmt->execute();
    $rows = $stmt->fetchAll();
    return $rows[0]['value'];
  }

  function getAll() {

    $db = ezcDbInstance::get();

    $q = $db->createSelectQuery();
    $e = $q->expr;
    $q->select( '*' )->from( 'settings' )
      ->orderBy( 'param' );
    $stmt = $q->prepare();
    $stmt->execute();

   $results = array();

    while ($row = $stmt->fetch())
      $results[$row['param']] = $row['value'];

    return $results;

  }


}


?>