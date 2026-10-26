// Optional, quiet environmental sound. Never starts without a user gesture.
export function createWindowAudio(){
 let audio,source,filter,level,lfo,lfoDepth,enabled=false,scene='original',volume=.25;
 function update(){
  if(!audio)return;
  const storm=scene==='storm',ocean=scene==='ocean';
  filter.type=ocean?'lowpass':storm?'lowpass':'bandpass';
  filter.frequency.setTargetAtTime(ocean?350:storm?1600:600,audio.currentTime,.5);
  filter.Q.value=ocean?.5:storm?.65:.3;
  // Quiet scenes have no noise bed; ambience is an optional layer beneath music.
  level.gain.setTargetAtTime(enabled?volume*(storm?.08:ocean?.028:0):0,audio.currentTime,.4);
  lfo.frequency.value=storm?.19:.07;lfoDepth.gain.value=storm?420:60;
 }
 async function toggle(){
  if(!audio){
   const Audio=window.AudioContext||window.webkitAudioContext;if(!Audio)return false;
   audio=new Audio();const buffer=audio.createBuffer(1,audio.sampleRate*8,audio.sampleRate),data=buffer.getChannelData(0);let last=0;
   for(let i=0;i<data.length;i++){last=(last+.025*(Math.random()*2-1))/1.025;data[i]=last*7;}
   source=audio.createBufferSource();source.buffer=buffer;source.loop=true;
   filter=audio.createBiquadFilter();level=audio.createGain();level.gain.value=0;
   lfo=audio.createOscillator();lfoDepth=audio.createGain();lfo.connect(lfoDepth);lfoDepth.connect(filter.frequency);
   source.connect(filter);filter.connect(level);level.connect(audio.destination);source.start();lfo.start();
  }
  await audio.resume();enabled=!enabled;update();return enabled;
 }
 document.addEventListener('visibilitychange',()=>{if(audio){if(document.hidden)audio.suspend();else if(enabled)audio.resume().catch(()=>{});}});
 window.addEventListener('pagehide',()=>audio?.close());
 return {toggle,setScene(id){scene=id;update();},setVolume(value){volume=Math.max(0,Math.min(1,Number(value)||0));update();}};
}
