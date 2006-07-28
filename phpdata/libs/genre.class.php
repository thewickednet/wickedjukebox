<?php

/**
 *
 *
 * @version $Id$
 * @copyright 2006
 */

class Genre {

  function getById($id = 0){

    $db = ezcDbInstance::get();

    $stmt = $db->prepare("SELECT * FROM genres WHERE genre_id = ?");
    $stmt->execute(array("$id"));

    return $stmt->fetchAll();
  }

  function getAll() {

    $db = ezcDbInstance::get();

    $results = array();

    $q = $db->createSelectQuery();
    $e = $q->expr;
    $q->select( '*' )->from( 'genres' )
      ->orderBy( 'name' );
    $stmt = $q->prepare();
    $stmt->execute();

    while ($row = $stmt->fetch())
      $results[$row['genre_id']] = $row['name'];

    return $results;

  }

}

?>