import {createWaterRipple,waveProgress} from './water-ripple.js';
// A is retained unchanged; the selected B has a refracting, decaying wave train.
export const TRANSITIONS=[['glitch','A · 方块错版','保留的 A 版：方块交错换色，带轻微横向错位。'],['ripple','B · 水波涟漪','从小铃荡开，先快后缓；波峰轻轻扭动画面，余波逐渐消散。']];
export function initTransitions(){
 const canvas=document.querySelector('#style-transition'),ctx=canvas.getContext('2d');
 const query=new URLSearchParams(location.search);
 let mode=TRANSITIONS.some(t=>t[0]===query.get('transition'))?query.get('transition'):'ripple';
 let water=null;
 try{water=createWaterRipple()}catch(error){console.warn('Water ripple fallback',error)}
 let frame=0,finish=null;
 const reduced=()=>matchMedia('(prefers-reduced-motion: reduce)').matches;
 function cancel(){cancelAnimationFrame(frame);canvas.hidden=true;if(finish){finish();finish=null}}
 function render(oldImage,newImage,t,kind){
  const w=canvas.width,h=canvas.height;
  if(kind==='ripple'&&water?.draw(ctx,t))return;
  ctx.clearRect(0,0,w,h);ctx.drawImage(newImage,0,0,w,h);
  if(kind==='glitch'){
   ctx.drawImage(oldImage,0,0,w,h);
   const cw=w/28,ch=h/16,peak=Math.sin(Math.PI*t);
   for(let y=0;y<16;y++)for(let x=0;x<28;x++){
    const hash=((Math.sin(x*127.1+y*311.7)*43758.5453)%1+1)%1;
    const group=((Math.sin(Math.floor(x/4)*53.2+Math.floor(y/4)*97.1)*19431.1)%1+1)%1;
    const order=hash*.6+group*.4;
    if(order>t*1.25-.12)continue;
    const dx=(hash>.78?(hash-.5)*20*peak:0),sx=x*cw,sy=y*ch;
    ctx.drawImage(newImage,sx,sy,cw,ch,sx+dx,sy,cw+1,ch+1);
    if(Math.abs(order-(t*1.25-.12))<.025){ctx.fillStyle='rgba(255,206,100,.24)';ctx.fillRect(sx,sy,cw+1,ch+1)}
   }
  }else if(kind==='ripple'){
   ctx.drawImage(oldImage,0,0,w,h);
   const ox=w*1195/1920,oy=h*538/1080,r=waveProgress(t)*(Math.hypot(Math.max(ox,w-ox),Math.max(oy,h-oy))+w*.13);
   ctx.save();ctx.beginPath();ctx.arc(ox,oy,r,0,Math.PI*2);ctx.clip();ctx.drawImage(newImage,0,0,w,h);ctx.restore();
   if(t>0&&t<1)for(let n=0;n<3;n++){ctx.beginPath();ctx.arc(ox,oy,Math.max(0,r-n*40),0,Math.PI*2);ctx.strokeStyle=`rgba(255,255,255,${.13*(1-t)/(n+1)})`;ctx.lineWidth=1;ctx.stroke()}
  }
 }
 async function play(oldImage,newImage){
  cancel();if(reduced())return;
  canvas.width=oldImage.naturalWidth;canvas.height=oldImage.naturalHeight;canvas.hidden=false;
  const kind=mode,duration=kind==='glitch'?700:1500;
  if(kind==='ripple'&&water)water.prepare(oldImage,newImage);
  const start=performance.now();
  canvas.dataset.renderer=kind==='ripple'&&water?'water-webgl':'canvas';
  document.body.dataset.transitionRunning=kind;
  return new Promise(resolve=>{finish=()=>{delete document.body.dataset.transitionRunning;resolve()};
   const tick=now=>{const t=Math.min(1,(now-start)/duration);render(oldImage,newImage,t,kind);if(t<1)frame=requestAnimationFrame(tick);else{canvas.hidden=true;const done=finish;finish=null;done()}};
   render(oldImage,newImage,0,kind);frame=requestAnimationFrame(tick);
  });
 }
 const tray=document.querySelector('#transition-compare');tray.hidden=!query.has('compare');
 const update=()=>{document.body.dataset.transitionMode=mode;tray.querySelectorAll('[data-transition]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.transition===mode)));document.querySelector('#transition-description').textContent=TRANSITIONS.find(t=>t[0]===mode)[2]};
 tray.querySelectorAll('[data-transition]').forEach(b=>b.addEventListener('click',()=>{mode=b.dataset.transition;update();const url=new URL(location.href);url.searchParams.set('transition',mode);history.replaceState(null,'',url);tray.dispatchEvent(new CustomEvent('preview-transition'))}));
 update();return {play,cancel};
}
