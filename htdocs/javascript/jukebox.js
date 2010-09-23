

function addsong(id) {

            $("#queue").load('/index.php?module=queue&action=addsong&param='+id);
  return false;

}

function addsplashsong(id) {

  $("#queue").load('/index.php?module=queue&action=addsong&mode=splash&param='+id);
  return false;

}

function delsong(id) {

  $("#queue").load('/index.php?module=queue&action=remove&param='+id);

}

function addalbum(id) {

  $("#queue").load('/index.php?module=queue&action=addalbum&param='+id);
  return false;

}

function queueArtistFavourites(id) {

    $("#queue").load('/index.php?module=queue&action=addartistfavourites&param='+id);
    return false;

}

function queueAlbumFavourites(id) {

    $("#queue").load('/index.php?module=queue&action=addalbumfavourites&param='+id);
    return false;

}

function cleanqueue(mode) {
    
     if (mode == 'splash') {
    $("#queue").load('/index.php?module=queue&action=clear&mode=splash');
     }
     else
         {
    $("#queue").load('/index.php?module=queue&action=clear');
         }
  return false;

}

function control(what){
    
  $.ajax({
   type: "GET",
   url: '/index.php?module=backenddb&action='+what
  });
  
  
}

function refreshQueue(mode){
     if (mode == 'splash') {
    $("#queue").load('/index.php?module=queue&mode=splash');
     }
     else
         {
    $("#queue").load('/index.php?module=queue');
         }
  return false;
}

function refreshRandom(mode){
    showRandomCarousel();
    $("#random").load('/index.php?module=song&action=randomize&mode='+mode, function(){
        hideRandomCarousel();
    });
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

function refreshPlayer(){
    
    $("#splashtop").load('/index.php?module=authrefresh&mode=splash');
    
  return false;
}

function refreshProfile(mode) {
  if (mode == 'splash') {
    $("#splashtop").load('/index.php?module=authrefresh&mode='+mode);
  } else {
    $("#login").load('/index.php?module=authrefresh&mode='+mode);
  }
  return false;
}


function setStandingAffects(action, mode) {
  if (mode == 'splash') {
    $("#splashtop").load('/index.php?module=user&action='+action+'&mode='+mode);
  } else {
    $("#login").load('/index.php?module=user&action='+action+'&mode='+mode);
  }
  return false;
}


function setStanding(song, standing,  mode) {
  if (mode == 'splash') {
	  $("#nowplaying").load('/index.php?module=splash&action=report&param='+song+'&standing='+standing);
  } else if (mode == 'detail') {
	  $("#body").load('/index.php?module=song&action=detail&param='+song+'&standing='+standing);
  } else {
	  $("#login").load('/index.php?module=song&action=report&song='+song+'&standing='+standing);
  }
	
  return false;
}


function getLyrics(song) {
          showLyricsCarousel();
	  $("#body").load('/index.php?module=song&action=detail&param='+song+'&getLyrics=true', function(){
		hideLyricsCarousel();
          });
	  return false;
	}


function setArtistStanding(artist, standing) {
	  if (confirm('Do you really want to set all songs of this artist to: ' + standing)) {
              	  $("#body").load('/index.php?module=artist&action=detail&param='+artist+'&standing='+standing+'&mode=artist');
	  }
	  return false;
}

function setAlbumStanding(album, standing) {
	  var module = document.helperform.module.value;
	  var action = document.helperform.action.value;
	  var param = document.helperform.param.value;
	  
	  if (confirm('Do you really want to set all songs of this album to: ' + standing)) {
            $("#body").load('/index.php?module='+module+'&action='+action+'&param='+param+'&standing='+standing+'&target='+album+'&mode=album');
	  }
	  return false;
}

function search(target){
  var pattern = document.searchform.pattern.value;
  var mode = document.searchform.mode.value;

  if (target == 'splash') {
      $("#splash").load('/index.php?module=search&pattern='+pattern+'&target='+target+'&action='+mode);
  } else {
      $("#body").load('/index.php?module=search&pattern='+pattern+'&target='+target+'&action='+mode);
  }
    return false;

}

function login() {
  var username = document.loginform.username.value;
  var password = hex_md5(document.loginform.password.value);

  $("#login").load('/index.php?module=auth&username='+username+'&password='+password);

  return false;

}

function logout() {
  $("#login").load('/index.php?module=auth&mode=logout');

  return false;

}

function loaded(id, src) {
  img = document.getElementById('img_' + id);
  img.src = src;
}


function listAlpha(alpha) {
    
  var module = document.helperform.active_node.value;
  
  $("#body").load('/browse/'+module+'/'+alpha+'/');
  return false;
    
}


function listSpecial(type) {
    
    $("#body").load('/browse/album/'+type+'/');
  return false;
    
}


function blaatOver(page) {
    
  var alpha = document.helperform.alpha.value;
  var module = document.helperform.active_node.value;
  
  $("#alpha_results").load('/'+module+'/browse/'+alpha+'/'+page+'/');
  
    
}


function blaatOverDetail(page) {

  var param = document.helperform.param.value;
  var module = document.helperform.module.value;

  $("#results").load('/?module='+module+'&action=detail&param='+param+'&pagenum='+page);

}


function blaatOverUser(page) {

  var param = document.helperform.param.value;
  var module = document.helperform.module.value;
  var action = document.helperform.action.value;

  $("#results").load('/?module='+module+'&action='+action+'&param='+param+'&pagenum='+page);

}


function blaatOverSearch(page, target) {

  var pattern = document.searchform.pattern.value;
  var mode = document.searchform.mode.value;

  if (target == 'splash') {
    $("#splash").load('/index.php?module=search&pattern='+pattern+'&action='+mode+'&target='+target+'&pagenum='+page);
  } else {
    $("#body").load('/index.php?module=search&pattern='+pattern+'&action='+mode+'&target='+target+'&pagenum='+page);
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


function showLyricsCarousel() {
	var loading = document.getElementById('lyrics_carousel');
	loading.style.display = 'block';

}


function hideLyricsCarousel() {
	var loading = document.getElementById('lyrics_carousel');
	loading.style.display = 'none';
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
    winPlayer = window.open('http://wickedjukebox.com/player/', 'wickedJukeboxPlayer', 'toolbar=0, location=0, scrollbars=0, resizable=0, menubar=0, status=0, width=320, height=280');
}


function shout() {
	
    var body = escape(document.shouter.body.value);
    document.shouter.body.value = '';
    $("#shoutboxmsgs").load('/?module=shoutbox&action=shout&body='+body);
    
    return false;
	
}


function shoutbox() {
	
    $("#shoutboxmsgs").load('/?module=shoutbox');
    
    return false;
	
}


function quicksearch() {
	
    var body = escape(document.qsearch.body.value);
    $("#qresults").load('/?module=splash&action=search&body='+body);
    
    return false;
	
}

function changeChannel() {
	
	var channel = document.getElementById('channel_changer');
	location.href = "/user/channel/?id=" + channel.value;
}


// added support for multiple counter spans with arbitrary direction
function counter() {
	var spans=document.getElementsByName('counter');
	for (var i=0;i<spans.length;i++){
		var counter=1*spans[i].getAttribute("sec");
		var inc=1*spans[i].getAttribute("inc");
		var max=1*spans[i].getAttribute("max");

		if ((inc<0 && counter>0) || (inc>0 && max>counter )) {
			counter=counter+inc;

			spans[i].setAttribute("sec",counter);
			var s=counter;
			var h=Math.round(Math.floor(s/(60.0*60.0)));
			s%=(60*60);
			var m=Math.round(Math.floor(s/60.0));
			s%=(60);
                        
                        s=Math.round(s);
                        
                        if (s>59)
                            {
                                s=0;
                                m=m+1;
                            }

                        if (s<10) {
				s="0"+s;
			}

                        if (m<10) {
                            m="0"+m;
			}
                        
                        
			try {
				if (h>0) {
					spans[i].innerHTML=h+":"+m+":"+s;
				}else{
					spans[i].innerHTML=m+":"+s;
				}
			}catch(err){} // ignore error
		}
                else
                    {
                        refreshPlayer();
                    }
	}
}


function autoRefreshSplash()
{

    $.doTimeout('autoRefresh', 10000, function(){
     $("#queue").load('/index.php?module=queue&action=refresh&mode=splash');
        return true;
    });


}