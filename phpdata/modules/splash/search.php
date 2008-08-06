<?

  $results = Search::bySong($_GET['body'], 15);

  $smarty->assign("QRESULTS", $results);
  $core->template = 'splash/qresults.tpl';

?>