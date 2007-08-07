

function addsong(id) {

  new Ajax.Updater('queue', '/index.php?module=queue&action=addsong&param='+id, {asynchronous:true, evalScripts:true });
  return false;

}

function delsong(id) {

  new Ajax.Updater('queue', '/index.php?module=queue&action=remove&param='+id, {asynchronous:true, evalScripts:true });
  return false;

}

function addalbum(id) {

  new Ajax.Updater('queue', '/index.php?module=queue&action=addalbum&param='+id, {asynchronous:true, evalScripts:true });
  return false;

}

function cleanqueue() {

  new Ajax.Updater('queue', '/index.php?module=queue&action=clear', {asynchronous:true, evalScripts:true });
  return false;

}

function control(what){
  new Ajax.Updater('queue', '/index.php?section=backend&param='+what, {asynchronous:true, evalScripts:true });
  return false;
}

function refreshQueue(){
  new Ajax.Updater('queue', '/index.php?module=queue', {asynchronous:true, evalScripts:true });
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

  new Ajax.Updater('login', '/index.php?module=auth&username='+username+'&password='+password, {asynchronous:true, evalScripts:true });
  return false;

}

function logout() {
  new Ajax.Updater('login', '/index.php?module=auth&mode=logout', {asynchronous:true, evalScripts:true });
  return false;

}

function loaded(id, src) {
  img = document.getElementById('img_' + id);
  img.src = src;
}



function updateQueue()
{
    var options = {
                    method : 'post',
                    parameters : Sortable.serialize('queue_list')
                  };
 
    new Ajax.Request('/?module=queue&action=resort', options);
}
