const $=selector=>document.querySelector(selector);
const near=$('#close-motion'),desk=$('#desk-motion'),videos=[near,desk],stage=$('#stage'),play=$('#pet-play'),pause=$('#pause-play'),slider=$('#timeline');
const videoUrls=[];
let active=near,playing=false,starting=false,frame=0,serial=0,ready=false,touchStart=null,armed=true;
export function motionLabel(seconds){return seconds<.65?'窝着休息':seconds<1.7?'慢慢起身':seconds<4.1?'塌腰，伸个懒腰':seconds<5?'收回前爪':'慢慢窝回去';}
function readout(){
 const time=active.currentTime,duration=active.duration||7.333;
 slider.value=Math.round(time/duration*1000);$('#time').textContent=`${time.toFixed(1)} / ${duration.toFixed(1)} 秒`;
 $('#motion-status').textContent=playing?motionLabel(time):time<.05?'窝着休息':time>duration-.12?'窝着休息':motionLabel(time)+' · 暂停';
}
function tick(){readout();if(playing)frame=requestAnimationFrame(tick);}
function stop(){serial++;videos.forEach(v=>v.pause());playing=starting=false;stage.dataset.playing='false';cancelAnimationFrame(frame);play.textContent='再摸摸它';pause.textContent='继续';readout();}
async function begin(reset=true){
 if(!ready||playing||starting)return;starting=true;const ticket=++serial,video=active;
 if(reset||video.currentTime>=video.duration-.1)video.currentTime=0;
 try{await video.play();if(ticket!==serial)return;starting=false;playing=true;stage.dataset.playing='true';play.textContent='正在伸懒腰…';pause.textContent='暂停';tick();}
 catch{if(ticket===serial){playing=starting=false;$('#motion-status').textContent='点一下“摸摸它”播放';}}
}
play.addEventListener('click',()=>begin(true));
pause.addEventListener('click',()=>playing?stop():begin(false));
$('#pet-target').addEventListener('click',()=>begin(true));
// Intentional movement across the cat feels like a stroke; merely entering does not play.
$('#pet-target').addEventListener('pointerenter',e=>{armed=true;touchStart=[e.clientX,e.clientY,performance.now()];});
$('#pet-target').addEventListener('pointermove',e=>{
 if(e.pointerType==='touch'||matchMedia('(prefers-reduced-motion: reduce)').matches||!armed||playing||!touchStart)return;
 if(Math.hypot(e.clientX-touchStart[0],e.clientY-touchStart[1])>22&&performance.now()-touchStart[2]>100){armed=false;begin(true);}
});
$('#pet-target').addEventListener('pointerleave',()=>{touchStart=null;armed=true;});
slider.addEventListener('input',()=>{const fraction=Number(slider.value)/1000;stop();active.currentTime=fraction*active.duration;readout();});
for(const v of videos){v.addEventListener('ended',()=>{if(v===active&&playing){stop();active.currentTime=0;readout();}});v.addEventListener('seeked',readout);v.addEventListener('error',()=>{$('#load-error').hidden=false;});}
async function view(close){
 const wasPlaying=playing,time=active.currentTime;stop();active=close?near:desk;active.currentTime=time;
 stage.classList.toggle('close-view',close);$('#close-view').setAttribute('aria-pressed',String(close));$('#desk-view').setAttribute('aria-pressed',String(!close));readout();if(wasPlaying)await begin(false);
}
$('#close-view').addEventListener('click',()=>view(true));$('#desk-view').addEventListener('click',()=>view(false));
document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});
document.addEventListener('keydown',e=>{if(e.key==='Escape')stop();});
window.addEventListener('pagehide',()=>{stop();videoUrls.forEach(url=>URL.revokeObjectURL(url));});
try{
 const response=await fetch('assets/cat-motion/motion.json');if(!response.ok)throw Error('metadata');const m=await response.json();
 Object.assign(desk.style,{left:`${m.crop[0]/1920*100}%`,top:`${m.crop[1]/1080*100}%`,width:`${m.width/1920*100}%`,height:`${m.height/1080*100}%`});
 // Local preview hosts may not implement byte ranges. A fully loaded Blob remains
 // seekable, so scrubbing and viewpoint switches work on those hosts as well.
 await Promise.all(videos.map(async v=>{
  const response=await fetch(v.querySelector('source').src);if(!response.ok)throw Error('video');
  const url=URL.createObjectURL(new Blob([await response.arrayBuffer()],{type:'video/mp4'}));videoUrls.push(url);
  await new Promise((resolve,reject)=>{v.addEventListener('loadeddata',resolve,{once:true});v.addEventListener('error',reject,{once:true});v.src=url;v.load();});
 }));
 ready=true;play.disabled=pause.disabled=false;play.textContent='摸摸它';readout();
}catch{$('#load-error').hidden=false;play.textContent='动作未加载';}
