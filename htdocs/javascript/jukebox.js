

function addsong(id) {

  new Ajax.Updater('queue', '/index.php?module=queue&action=addsong&param='+id, {asynchronous:true, evalScripts:true });
  return false;

}


function delsong(id) {
  QueueUpdates.stop();
  Effect.Fade('queue_' + id);
  new Ajax.Request('/index.php?module=queue&action=remove&param='+id, {asynchronous:true, evalScripts:true });
  QueueUpdates.start();
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
  new Ajax.Request('/index.php?module=backend&action='+what, {asynchronous:true, evalScripts:true });
}

function refreshQueue(){
  new Ajax.Updater('queue', '/index.php?module=queue', {asynchronous:true, evalScripts:true });
  return false;
}

function refreshQueuePeriodical(){
  QueueUpdates = new Ajax.PeriodicalUpdater('queue', '/index.php?module=queue', { method: 'get', frequency: 10, decay: 1, asynchronous:true, evalScripts:true });
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


function listAlpha(alpha) {
    
  var module = document.helperform.active_node.value;
  
  new Ajax.Updater('body', '/browse/'+module+'/'+alpha+'/', {asynchronous:true, evalScripts:true });
  return false;
    
}

function blaatOver(page) {
    
  var alpha = document.helperform.alpha.value;
  var module = document.helperform.active_node.value;
  
  new Ajax.Updater('alpha_results', '/browse/'+module+'/'+alpha+'/bypage/'+page+'/', {asynchronous:true, evalScripts:true });
    
}

function resortQueue()
{
    var options = {
                    method : 'post',
                    parameters : Sortable.serialize('queue_list')
                  };
 
    new Ajax.Request('/?module=queue&action=resort', options);
}
