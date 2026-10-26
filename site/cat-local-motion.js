export function phaseAt(t){return t<.4?'rest':t<2.25?'rise':t<5.8?'groom':'settle';}
export function createCatHoverGate(){
 let inside=false;
 return {enter(hit,enabled=true){const trigger=hit&&!inside&&enabled;inside=hit;return trigger;},leave(){inside=false;}};
}
export function createCatPlayback(duration=8){
 let time=0,playing=false;
 return {
  get time(){return time;},get playing(){return playing;},
  touch(){if(playing)return false;time=0;playing=true;return true;},
  pause(){playing=false;},resume(){if(time>=duration)time=0;playing=true;},
  seek(t){playing=false;time=Math.max(0,Math.min(duration,t));},
  update(dt){if(!playing)return false;time+=Math.max(0,dt);if(time>=duration){time=0;playing=false;}return true;}
 };
}
