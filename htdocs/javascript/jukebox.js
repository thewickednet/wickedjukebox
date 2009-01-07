

function addsong(id) {

  new Ajax.Updater('queue', '/index.php?module=queue&action=addsong&param='+id, {asynchronous:true, evalScripts:true });
  return false;

}

function addsplashsong(id) {

  new Ajax.Updater('queue', '/index.php?module=queue&action=addsong&mode=splash&param='+id, {asynchronous:true, evalScripts:true });
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

function refreshQueue(mode){
  new Ajax.Updater('queue', '/index.php?module=queue&mode='+mode, {asynchronous:true, evalScripts:true });
  return false;
}

function refreshRandom(mode){
  new Ajax.Updater('random', '/index.php?module=song&action=randomize&mode='+mode, {asynchronous:true, evalScripts:true, onLoading: showRandomCarousel, onComplete: hideRandomCarousel });
  return false;
}

function refreshQueuePeriodical(mode){
  QueueUpdates = new Ajax.PeriodicalUpdater('queue', '/index.php?module=queue&action=refresh&mode='+mode, { method: 'get', frequency: 10, decay: 1, asynchronous:true, evalScripts:true });
  return false;
}

function refreshPlayerPeriodical(){
  PlayerUpdates = new Ajax.PeriodicalUpdater('playerInfo', '/index.php?module=player&action=update', { method: 'get', frequency: 10, decay: 1, asynchronous:true, evalScripts:true });
  return false;
}

function refreshProfile(mode) {
  if (mode == 'splash') {
    new Ajax.Updater('splashtop', '/index.php?module=authrefresh&mode='+mode, {asynchronous:true, evalScripts:true });
  } else {
    new Ajax.Updater('login', '/index.php?module=authrefresh&mode='+mode, {asynchronous:true, evalScripts:true });
  }
  return false;
}


function setStandingAffects(action, mode) {
  if (mode == 'splash') {
    new Ajax.Updater('splashtop', '/index.php?module=user&action='+action+'&mode='+mode, {asynchronous:true, evalScripts:true });
  } else {
    new Ajax.Updater('login', '/index.php?module=user&action='+action+'&mode='+mode, {asynchronous:true, evalScripts:true });
  }
  return false;
}


function setStanding(song, standing,  mode) {
  if (mode == 'splash') {
	  new Ajax.Updater('nowplaying', '/index.php?module=splash&action=report&param='+song+'&standing='+standing, {asynchronous:true, evalScripts:true });
  } else if (mode == 'detail') {
	  new Ajax.Updater('body', '/index.php?module=song&action=detail&param='+song+'&standing='+standing, {asynchronous:true, evalScripts:true });
  } else {
	  new Ajax.Updater('login', '/index.php?module=song&action=report&song='+song+'&standing='+standing, {asynchronous:true, evalScripts:true });
  }
	
  return false;
}

function setArtistStanding(artist, standing) {
	  if (confirm('Do you really want to set all songs of this artist to: ' + standing)) {
		  new Ajax.Updater('body', '/index.php?module=artist&action=detail&param='+artist+'&standing='+standing+'&mode=artist', {asynchronous:true, evalScripts:true });
	  }
	  return false;
}

function setAlbumStanding(album, standing) {
	  var module = document.helperform.module.value;
	  var action = document.helperform.action.value;
	  var param = document.helperform.param.value;
	  
	  if (confirm('Do you really want to set all songs of this album to: ' + standing)) {
		  new Ajax.Updater('body', '/index.php?module='+module+'&action='+action+'&param='+param+'&standing='+standing+'&target='+album+'&mode=album', {asynchronous:true, evalScripts:true });
	  }
	  return false;
}

function search(target){
  var pattern = document.searchform.pattern.value;
  var mode = document.searchform.mode.value;

  if (target == 'splash') {
    new Ajax.Updater('splash', '/index.php?module=search&pattern='+pattern+'&target='+target+'&action='+mode, {asynchronous:true, evalScripts:true, onLoading: showSearchCarousel, onComplete: hideSearchCarousel });
  } else {
    new Ajax.Updater('body', '/index.php?module=search&pattern='+pattern+'&target='+target+'&action='+mode, {asynchronous:true, evalScripts:true, onLoading: showSearchCarousel, onComplete: hideSearchCarousel });
  }
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


function listSpecial(type) {
    
  new Ajax.Updater('body', '/browse/album/'+type+'/', {asynchronous:true, evalScripts:true });
  return false;
    
}


function blaatOver(page) {
    
  var alpha = document.helperform.alpha.value;
  var module = document.helperform.active_node.value;
  
  new Ajax.Updater('alpha_results', '/'+module+'/browse/'+alpha+'/'+page+'/', {asynchronous:true, evalScripts:true });
    
}


function blaatOverDetail(page) {

  var param = document.helperform.param.value;
  var module = document.helperform.module.value;

  new Ajax.Updater('results', '/?module='+module+'&action=detail&param='+param+'&pagenum='+page, {asynchronous:true, evalScripts:true });

}


function blaatOverUser(page) {

  var param = document.helperform.param.value;
  var module = document.helperform.module.value;
  var action = document.helperform.action.value;

  new Ajax.Updater('results', '/?module='+module+'&action='+action+'&param='+param+'&pagenum='+page, {asynchronous:true, evalScripts:true });

}


function blaatOverSearch(page, target) {

  var pattern = document.searchform.pattern.value;
  var mode = document.searchform.mode.value;

  if (target == 'splash') {
    new Ajax.Updater('splash', '/index.php?module=search&pattern='+pattern+'&action='+mode+'&target='+target+'&pagenum='+page, {asynchronous:true, evalScripts:true, onLoading: showSearchCarousel, onComplete: hideSearchCarousel });
  } else {
    new Ajax.Updater('body', '/index.php?module=search&pattern='+pattern+'&action='+mode+'&target='+target+'&pagenum='+page, {asynchronous:true, evalScripts:true, onLoading: showSearchCarousel, onComplete: hideSearchCarousel });
  }

}


function resortQueue()
{
    var options = {
                    method : 'post',
                    parameters : Sortable.serialize('queue_list')
                  };
 
    new Ajax.Request('/?module=queue&action=resort', options);
}


function showSearchCarousel() {
	var loading = document.getElementById('search_carousel');
	loading.style.display = 'block';

}


function hideSearchCarousel() {
	var loading = document.getElementById('search_carousel');
	loading.style.display = 'none';
}


function showRandomCarousel() {
	var loading = document.getElementById('random_carousel');
	loading.style.display = 'block';

}


function hideRandomCarousel() {
	var loading = document.getElementById('random_carousel');
	loading.style.display = 'none';
}


function showQSearchCarousel() {
	var loading = document.getElementById('qsearch_carousel');
	loading.style.display = 'block';

}


function hideQSearchCarousel() {
	var loading = document.getElementById('qsearch_carousel');
	loading.style.display = 'none';
}


function openPlayer() {
    winPlayer = window.open('http://jukebox.wicked.lu/player/', 'wickedJukeboxPlayer', 'toolbar=0, location=0, scrollbars=0, resizable=0, menubar=0, status=0, width=320, height=280');
}


function shout() {
	
	var body = escape(document.shouter.body.value);
	document.shouter.body.value = '';
	new Ajax.Updater('shoutboxmsgs', '/?module=shoutbox&action=shout&body='+body, {asynchronous:true, evalScripts:true });
    
    return false;
	
}


function shoutbox() {
	
	new Ajax.PeriodicalUpdater('shoutboxmsgs', '/?module=shoutbox', {asynchronous:true, evalScripts:true, frequency: 5, decay: 1 });
    
    return false;
	
}


function quicksearch() {
	
	var body = escape(document.qsearch.body.value);
	new Ajax.Updater('qresults', '/?module=splash&action=search&body='+body, {asynchronous:true, evalScripts:true, onLoading: showQSearchCarousel, onComplete: hideQSearchCarousel });
    
    return false;
	
}
