var AudioPlayer=function(){var F=[];var E;var C="";var A={};var B=-1;var D=function(G){return document.all?window[G]:document[G]};return{setup:function(H,G){C=H;A=G},embed:function(K,O){var I={};var M;var G;var P;var H;var N={};var J={};var L={};for(M in A){I[M]=A[M]}for(M in O){I[M]=O[M]}if(I.transparentpagebg=="yes"){N.bgcolor="#FFFFFF";N.wmode="transparent"}else{if(I.pagebg){N.bgcolor="#"+I.pagebg}N.wmode="opaque"}N.menu="false";for(M in I){if(M=="pagebg"||M=="width"||M=="transparentpagebg"){continue}J[M]=I[M]}L.name=K;L.style="outline: none";J.playerID=K;swfobject.embedSWF(C,K,I.width.toString(),"24","9.0.0",false,J,N,L);F.push(K)},syncVolumes:function(G,I){B=I;for(var H=0;H<F.length;H++){if(F[H]!=G){D(F[H]).setVolume(B)}}},activate:function(G){if(E&&E!=G){D(E).closePlayer()}E=G},getVolume:function(G){return B}}}()