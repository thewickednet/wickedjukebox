

function addsong(id) {

  new Ajax.Updater('queue', '/index.php?section=queue&module=song&mode=add&ajax=1&param='+id, {asynchronous:true, evalScripts:true });
  return false;

}

function delsong(id) {

  new Ajax.Updater('queue', '/index.php?section=queue&module=song&mode=del&ajax=1&param='+id, {asynchronous:true, evalScripts:true });
  return false;

}

function addalbum(id) {

  new Ajax.Updater('queue', '/index.php?section=queue&module=album&mode=add&ajax=1&param='+id, {asynchronous:true, evalScripts:true });
  return false;

}

function delalbum(id) {

  new Ajax.Updater('queue', '/index.php?section=queue&module=album&mode=del&ajax=1&param='+id, {asynchronous:true, evalScripts:true });
  return false;

}

function cleanqueue() {

  new Ajax.Updater('queue', '/index.php?section=queue&module=queue&mode=clean&ajax=1', {asynchronous:true, evalScripts:true });
  return false;

}
