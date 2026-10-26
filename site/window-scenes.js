import {WINDOW_SCENES,paintWindow} from './window-art.js';
import {windowForStyle} from './style-window.js';
import {createWindowAudio} from './window-audio.js';
import {createMusicPlayer} from './music.js';
import {loadDetailedWindow} from './window-detail.js';
import {windowGlassStyle,paintWindowGlass} from './window-glass.js';
export function createWindowScenes({enabled=true}={}){
 const canvas=document.querySelector('#window-scene'),ctx=canvas.getContext('2d');
 const current=document.querySelector('#window-current'),sound=document.querySelector('#window-sound'),status=document.querySelector('#window-status');
 const mask=new Image(),audio=createWindowAudio(),reduced=matchMedia('(prefers-reduced-motion: reduce)');
 const music=createMusicPlayer({setAmbientVolume:audio.setVolume});
 const work=document.createElement('canvas'),wc=work.getContext('2d');
 const grain=document.createElement('canvas');grain.width=grain.height=96;const gc=grain.getContext('2d'),noise=gc.createImageData(96,96);
 let seed=27183;
 for(let i=0;i<noise.data.length;i+=4){seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;const v=(seed>>>0)%97;noise.data[i]=noise.data[i+1]=noise.data[i+2]=v>48?255:0;noise.data[i+3]=v%16;}
 gc.putImageData(noise,0,0);
 let scene='original',ready=false,raf=0,last=0,elapsed=0,previousTime=0;
 canvas.width=1920;canvas.height=1080;
 document.querySelector('#window-controls').hidden=!enabled;
 function renderInto(target,style,time,scenery=scene){
  const pixel=style==='pixel',width=pixel?384:1280,height=width*9/16;
  if(work.width!==width){work.width=width;work.height=height;}
  wc.setTransform(width/1920,0,0,width/1920,0,0);paintWindow(wc,scenery,time,style);
  const tc=target.getContext('2d');tc.clearRect(0,0,1920,1080);tc.imageSmoothingEnabled=!pixel;
  tc.filter=windowGlassStyle(scenery,style).filter;
  tc.drawImage(work,0,0,1920,1080);tc.filter='none';
  paintWindowGlass(tc,scenery,style);
  tc.save();tc.globalAlpha=.25;tc.fillStyle=tc.createPattern(grain,'repeat');tc.fillRect(0,0,1920,1080);tc.restore();
  tc.globalCompositeOperation='destination-in';tc.drawImage(mask,0,0);tc.globalCompositeOperation='source-over';
 }
 function draw(){if(!ready||scene==='original')return;renderInto(canvas,document.body.dataset.style||'original',elapsed);canvas.dataset.scene=scene;}
 function loop(now){
  if(document.hidden){raf=0;previousTime=0;return;}
  if(previousTime)elapsed+=Math.min((now-previousTime)/1000,.1);previousTime=now;
  if(now-last>41){last=now;draw();}
  if(!reduced.matches&&scene!=='original')raf=requestAnimationFrame(loop);else raf=0;
 }
 function resume(){cancelAnimationFrame(raf);previousTime=0;draw();if(!document.hidden&&!reduced.matches&&scene!=='original')raf=requestAnimationFrame(loop);}
 async function prepareStyle(style){
  if(!enabled||!ready)return ()=>{};
  const requested=windowForStyle(style);
  if(['sunset','ocean'].includes(requested)){
   try{await loadDetailedWindow(requested);}catch(error){console.warn('Using the simplified matching window scenery.',error);}
  }
  // No visible mutation until the style controller commits the same request.
  return ()=>{
   scene=requested;elapsed=0;canvas.hidden=false;document.body.dataset.windowScene=scene;
   audio.setScene(scene);music.setScene(scene);sound.disabled=false;
   current.textContent=`窗外 · ${WINDOW_SCENES.find(s=>s.id===scene).name} · 随画风`;
   const url=new URL(location.href);url.searchParams.set('window',scene);history.replaceState(null,'',url);
   resume();status.textContent='';
  };
 }
 sound.addEventListener('click',async()=>{try{const active=await audio.toggle();sound.setAttribute('aria-pressed',String(active));sound.textContent=active?'环境声 开':'环境声 关';}catch{status.textContent='当前设备暂时无法播放环境声。';}});
 document.addEventListener('visibilitychange',()=>{if(!document.hidden)resume();});reduced.addEventListener('change',resume);
 window.addEventListener('pagehide',()=>cancelAnimationFrame(raf));
 return {
  async init(){if(!enabled)return;try{mask.src='assets/windows/aperture.png';await mask.decode();ready=true;}catch{status.textContent='窗景暂未加载，已保留原来的窗外。';canvas.hidden=true;}},
  prepareStyle,
  refresh(){draw();},
  compose(image,style){
   if(!ready)return image;
   const layer=document.createElement('canvas');layer.width=1920;layer.height=1080;renderInto(layer,style,elapsed,windowForStyle(style));
   const result=document.createElement('canvas');result.width=result.naturalWidth=1920;result.height=result.naturalHeight=1080;
   const c=result.getContext('2d');c.drawImage(image,0,0,1920,1080);c.drawImage(layer,0,0);return result;
  }
 };
}
