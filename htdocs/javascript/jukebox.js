

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

function control(what){
  new Ajax.Updater('queue', '/index.php?section=backend&param='+what, {asynchronous:true, evalScripts:true });
  return false;
}



function refreshQueue(){
  new Ajax.Updater('queue', '/index.php?section=queue&ajax=1', {asynchronous:true, evalScripts:true });
  return false;
}

function search(){
  var pattern = document.searchform.pattern.value;
  var mode = document.searchform.mode.value;

  new Ajax.Updater('mainbar', '/index.php?section=search&pattern='+pattern+'&mode='+mode, {asynchronous:true, evalScripts:true });
  return false;

}

function login() {
  var username = document.loginform.username.value;
  var password = hex_md5(document.loginform.password.value);

  new Ajax.Updater('login', '/index.php?section=login&ajax=1&username='+username+'&password='+password, {asynchronous:true, evalScripts:true });
  return false;

}

function logout() {
  new Ajax.Updater('login', '/index.php?section=login&ajax=1&mode=logout', {asynchronous:true, evalScripts:true });
  return false;

}

  function loaded(id, src) {
    img = document.getElementById('img_' + id);
    img.src = src;
  }

