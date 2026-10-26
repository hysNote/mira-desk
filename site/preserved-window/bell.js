// Actual recordings of Mira's own bell; only play after a click or key press.
const SOUND='assets/audio/bell-single.wav';
export function ringBell(){
 const player=document.querySelector('#bell-audio');if(!player)return;
 player.pause();player.src=SOUND;player.currentTime=0;player.volume=.85;
 const status=document.querySelector('#bell-audio-status');
 player.play().then(()=>{if(status)status.textContent=''}).catch(error=>{
  // Rapid presses intentionally interrupt the preceding playback.
  if(error.name!=='AbortError'&&status)status.textContent='暂时无法播放铃声，画风仍可正常切换。';
 });
}
