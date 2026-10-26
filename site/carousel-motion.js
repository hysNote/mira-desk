// These frames are rendered by Blender around the real carrier's vertical axis.
// The crown, pedestal, camera and scene stay fixed; no planar CSS rotation.
export function carrierProgress(t){
 t=Math.max(0,Math.min(1,t));
 return t*t*t*(t*(t*6-15)+10);
}
export function createCarouselMotion({enabled=true}={}){
 const canvas=document.querySelector('#carousel-motion'),ctx=canvas.getContext('2d');
 const status=document.querySelector('#carousel-status'),cache=new Map();
 let metadata,serial=0,raf=0,pending=null,resolvePending=null,fade=null;
 const reduced=()=>matchMedia('(prefers-reduced-motion: reduce)').matches;
 async function asset(){
  metadata??=fetch('assets/carousel/motion.json').then(r=>{if(!r.ok)throw Error('Carousel metadata');return r.json()}).catch(e=>{metadata=null;throw e});
  const m=await metadata,style=document.body.dataset.style||'original';
  if(!cache.has(style)){
   const image=new Image();image.src=`assets/carousel/${style}.webp`;
   cache.set(style,image.decode().then(()=>image).catch(e=>{cache.delete(style);throw e}));
   if(cache.size>3)cache.delete(cache.keys().next().value);
  }
  return {m,image:await cache.get(style)};
 }
 function cancel({soft=false}={}){
  serial++;cancelAnimationFrame(raf);fade?.cancel();fade=null;
  resolvePending?.(false);resolvePending=null;pending=null;
  delete document.body.dataset.carouselRunning;status.textContent='';
  if(soft&&!canvas.hidden&&!reduced()){
   const animation=canvas.animate([{opacity:1},{opacity:0}],{duration:220});fade=animation;
   animation.onfinish=()=>{if(fade===animation){canvas.hidden=true;fade=null;}};
  }else canvas.hidden=true;
 }
 function play(){
  if(pending)return pending;
  cancel();
  if(!enabled||reduced())return Promise.resolve(true);
  const ticket=serial;
  document.body.dataset.carouselRunning='loading';status.textContent='正在转动照片…';
  pending=new Promise(resolve=>{resolvePending=resolve;});const result=pending;
  let timeout;
  Promise.race([asset(),new Promise((_,reject)=>{timeout=setTimeout(()=>reject(Error('Carousel load timeout')),8000)})]).then(({m,image})=>{
   clearTimeout(timeout);if(ticket!==serial)return;
   const [x0,y0]=m.crop,[cw,ch]=m.canvas;
   canvas.width=m.width;canvas.height=m.height;
   Object.assign(canvas.style,{left:`${x0/cw*100}%`,top:`${y0/ch*100}%`,width:`${m.width/cw*100}%`,height:`${m.height/ch*100}%`});
   canvas.hidden=false;document.body.dataset.carouselRunning='playing';status.textContent='';
   const start=performance.now();
   function draw(frame,alpha=1){ctx.globalAlpha=alpha;ctx.drawImage(image,(frame%m.columns)*m.width,Math.floor(frame/m.columns)*m.height,m.width,m.height,0,0,m.width,m.height);}
   function tick(now){
    if(ticket!==serial)return;
    const t=Math.min(1,(now-start)/m.duration_ms),position=carrierProgress(t)*(m.frames-1),a=Math.floor(position);
    draw(a);if(a<m.frames-1)draw(a+1,position-a);ctx.globalAlpha=1;
    canvas.dataset.frame=String(a);
    if(t<1)raf=requestAnimationFrame(tick);
    else{delete document.body.dataset.carouselRunning;status.textContent='';const done=resolvePending;resolvePending=null;pending=null;done?.(true);}
   }
   tick(start);
  }).catch(error=>{
   clearTimeout(timeout);if(ticket!==serial)return;
   console.warn('Carousel animation unavailable; opening photos directly.',error);
   delete document.body.dataset.carouselRunning;status.textContent='';canvas.hidden=true;
   const done=resolvePending;resolvePending=null;pending=null;done?.(true);
  });
  return result;
 }
 document.addEventListener('keydown',event=>{if(event.key==='Escape'&&pending){event.preventDefault();cancel();}});
 window.addEventListener('pagehide',()=>cancel());
 return {play,cancel,warm(){if(enabled&&!reduced())asset().catch(()=>{});},get running(){return Boolean(pending);}};
}
