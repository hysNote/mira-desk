// Local, attributed CC BY 4.0 recordings. Nothing plays before an explicit gesture.
export const TRACKS = [
 {id:'bossa',label:'A · 温暖 Bossa Nova',title:'Bossa Antigua',file:'Bossa Antigua.mp3',isrc:'USUAN1700069',description:'吉他、贝斯与轻鼓点，像窗边的悠闲午后。'},
 {id:'guitar',label:'B · 轻柔木吉他',title:'Laid Back Guitars',file:'Laid Back Guitars.mp3',isrc:'USUAN1100181',description:'两把西班牙吉他与轻打击乐，松弛、亲近。'},
 {id:'dream',label:'C · 梦幻氛围',title:'Dreams Become Real',file:'Dreams Become Real.mp3',isrc:'USUAN1500027',description:'缓慢的钢琴与合成器，适合海底和雪景。'}
];
export const SCENE_MUSIC = Object.freeze({original:'bossa',sunset:'bossa',rainbow:'guitar',storm:'guitar',snow:'dream',ocean:'dream'});
export const musicForScene=scene=>SCENE_MUSIC[scene]||'bossa';

// A small crossfade mixer. Pending play promises are invalidated on stop/change.
export function createMusicMixer({makeAudio=src=>new Audio(src),now=()=>performance.now(),frame=requestAnimationFrame,cancel=cancelAnimationFrame,onState=()=>{}}={}){
 let selected=null,enabled=false,volume=.32,serial=0,raf=0,hidden=false;
 const voices=new Set();
 const emit=(status,message='')=>onState({status,message,enabled,track:selected});
 function dispose(v){v.audio.pause();v.audio.removeAttribute('src');v.audio.load();voices.delete(v);}
 function ramp(v,target){v.from=v.audio.volume;v.to=target;v.at=now();}
 function tick(){
  raf=0;
  for(const v of voices){
   const t=Math.min(1,(now()-v.at)/2000),ease=t*t*(3-2*t);
   v.audio.volume=Math.max(0,Math.min(1,v.from+(v.to-v.from)*ease));
   if(t===1&&v.to===0&&v.retiring)dispose(v);
   else if(t<1&&!raf)raf=frame(tick);
  }
 }
 function animate(){if(!raf)raf=frame(tick);}
 async function start(id){
  const track=TRACKS.find(t=>t.id===id);if(!track)return;
  selected=id;const ticket=++serial;enabled=true;emit('loading');
  const existing=[...voices].find(v=>v.id===id&&!v.retiring&&!v.pending);
  if(existing){emit(hidden?'paused':'playing');return;}
  // Retain the audible voice until the replacement has actually started.
  for(const v of [...voices])if(v.pending)dispose(v);
  const audio=makeAudio('assets/audio/music/'+encodeURIComponent(track.file));
  audio.loop=true;audio.preload='none';audio.volume=0;
  const voice={id,audio,from:0,to:0,at:now(),pending:true,retiring:false};voices.add(voice);
  try{
   await audio.play();
   if(ticket!==serial||!enabled){dispose(voice);return;}
   voice.pending=false;if(hidden)audio.pause();
   for(const v of voices){v.retiring=v!==voice;ramp(v,v===voice?volume:0);}
   animate();emit(hidden?'paused':'playing');
  }catch(error){
   dispose(voice);if(ticket!==serial)return;
   enabled=false;for(const v of [...voices])dispose(v);
   emit('error','音乐暂未播放，请再点一次播放。');
  }
 }
 function stop(){++serial;enabled=false;for(const v of [...voices]){if(v.pending)dispose(v);else{v.retiring=true;ramp(v,0);}}animate();emit('off');}
 return {
  start,stop,
  select(id){selected=id;if(enabled)return start(id);emit('off');},
  toggle(id){return enabled?stop():start(id);},
  setVolume(value){volume=Math.max(0,Math.min(1,Number(value)||0));for(const v of voices)if(!v.pending)ramp(v,v.retiring?0:volume);animate();},
  async setHidden(value){hidden=value;if(hidden){for(const v of voices)v.audio.pause();if(enabled)emit('paused');}
   else if(enabled){try{await Promise.all([...voices].filter(v=>!v.pending).map(v=>v.audio.play()));if(enabled)emit('playing');}catch{stop();emit('error','点击播放，继续听音乐。');}}},
  destroy(){++serial;enabled=false;cancel(raf);for(const v of [...voices])dispose(v);},
  getState(){return {enabled,selected,voices:voices.size};}
 };
}

export function createMusicPlayer({setAmbientVolume=()=>{}}={}){
 const $=s=>document.querySelector(s),panel=$('#audio-panel'),choices=$('#music-choices'),toggle=$('#music-toggle'),follow=$('#music-follow');
 let scene='original',selection='auto',current='bossa';
 const mixer=createMusicMixer({onState(state){
  panel.dataset.playing=String(state.enabled);
  toggle.setAttribute('aria-pressed',String(state.enabled));
  toggle.textContent=state.enabled?'暂停音乐':'播放音乐';
  $('#music-status').textContent=state.message||({loading:'正在加载音乐…',playing:'正在播放',paused:'已随页面暂歇',off:'点播放开始试听'}[state.status]);
 }});
 choices.innerHTML=TRACKS.map(t=>`<button type="button" data-music="${t.id}" aria-pressed="false"><strong>${t.label}</strong><small>${t.description}</small></button>`).join('');
 function update(){
  current=selection==='auto'?musicForScene(scene):selection;
  const t=TRACKS.find(t=>t.id===current);
  follow.setAttribute('aria-pressed',String(selection==='auto'));
  choices.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.music===current)));
  $('#music-title').textContent=t.title;
  $('#music-source').href='https://incompetech.com/music/royalty-free/index.html?isrc='+t.isrc;
  $('#music-mode').textContent=selection==='auto'?'随画风搭配':'固定试听 · 切换画风不换曲';
  $('#ambient-note').textContent=scene==='storm'?'轻风雨底音 · 合成环境声':scene==='ocean'?'低柔水声 · 合成环境声':'这个窗景保持安静，不添加沙沙声';
 }
 choices.addEventListener('click',e=>{const b=e.target.closest('[data-music]');if(!b)return;selection=b.dataset.music;update();mixer.start(current);});
 follow.addEventListener('click',()=>{selection='auto';update();mixer.select(current);});
 toggle.addEventListener('click',()=>mixer.toggle(current));
 $('#music-volume').addEventListener('input',e=>{mixer.setVolume(e.target.value/100);$('#music-volume-value').textContent=e.target.value+'%';});
 $('#ambient-volume').addEventListener('input',e=>{setAmbientVolume(e.target.value/100);$('#ambient-volume-value').textContent=e.target.value+'%';});
 $('#music-close').addEventListener('click',()=>{panel.open=false;panel.querySelector('summary').focus();});
 document.addEventListener('pointerdown',e=>{if(panel.open&&!panel.contains(e.target))panel.open=false;});
 panel.addEventListener('keydown',e=>{if(e.key==='Escape'){panel.open=false;panel.querySelector('summary').focus();}});
 document.addEventListener('visibilitychange',()=>mixer.setHidden(document.hidden));
 window.addEventListener('pagehide',()=>mixer.destroy());
 update();
 return {setScene(id){scene=id;update();mixer.select(current);}};
}
