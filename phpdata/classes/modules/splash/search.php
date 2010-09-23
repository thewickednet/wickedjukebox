<?

  $results = Search::bySong($_GET['body'], 15, true);

  $smarty->assign("QRESULTS", $results);
  $core->template = 'splash/qresults.tpl';

