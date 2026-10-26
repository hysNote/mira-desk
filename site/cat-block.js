/* Official public Sketchfab viewer; no protected asset extraction. */
const modelId='72a1b178705642e0a61cbb10003d38bd';
const status=document.querySelector('#status'),buttons=[...document.querySelectorAll('button')];
const names={'lying-sleep':'窝着睡觉','lying-down':'趴卧 ①','lying-down2':'趴卧 ②','sit-licking':'坐着舔毛'};
let api,clips=[],active='',paused=false,returnToSleep=false,generation=0;
if(new URLSearchParams(location.search).get('embed')==='1')document.body.classList.add('embedded');
function fail(){status.textContent='在线模型暂时无法连接，请刷新重试，或打开下方作者页面。';buttons.forEach(b=>b.disabled=true);}
function showState(){status.textContent=(names[active]||active)+(paused?' · 已暂停':' · 原作者动作');document.querySelectorAll('[data-clip]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.clip===active)));document.querySelector('#pause').textContent=paused?'继续':'暂停';}
function choose(name,once=false){
 const clip=clips.find(c=>c[1]===name);if(!api||!clip)return;
 const request=++generation;returnToSleep=once;active=name;paused=false;
 api.pause(()=>api.setCurrentAnimationByUID(clip[0],err=>{
  if(request!==generation)return;if(err){fail();return;}
  api.seekTo(0,()=>{if(request!==generation)return;api.setCycleMode(once?'one':'loopOne',()=>{if(request===generation){api.play();showState();}});});
 }));
}
document.querySelectorAll('[data-clip]').forEach(b=>b.onclick=()=>choose(b.dataset.clip));
document.querySelector('#pet').onclick=()=>choose('sit-licking',true);
document.querySelector('#pause').onclick=()=>{if(!api)return;paused=!paused;api[paused?'pause':'play']();showState();};
document.addEventListener('visibilitychange',()=>{if(document.hidden&&api){api.pause();paused=true;showState();}});
window.addEventListener('pagehide',()=>{generation++;api?.stop();});
if(typeof Sketchfab==='undefined')fail();else{
 new Sketchfab('1.12.1',document.querySelector('#block-viewer')).init(modelId,{
  autostart:1,animation_autoplay:0,camera:0,dnt:1,
  success(viewer){api=viewer;api.addEventListener('viewerready',()=>{
   api.setBackground({color:[.82,.84,.79]});
   api.getCameraLookAt((err,camera)=>{if(err)return;const distance=Math.hypot(...camera.position.map((v,i)=>v-camera.target[i]));camera.position[2]-=distance*.12;camera.target[2]-=distance*.12;api.setCameraLookAt(camera.position,camera.target,0);});
   api.getAnimations((err,list)=>{
    if(err||!list?.length){fail();return;}clips=list;
    buttons.forEach(b=>{b.disabled=b.dataset.clip?!clips.some(c=>c[1]===b.dataset.clip):false;});
    document.querySelector('#pet').disabled=!clips.some(c=>c[1]==='sit-licking');
    // Visible diagnostics record exactly which author clips are available.
    document.querySelector('.stage').dataset.clips=JSON.stringify(clips);
    choose('lying-sleep');
   });
  });api.addEventListener('animationEnded',()=>{if(returnToSleep&&!paused){returnToSleep=false;choose('lying-sleep');}});
  api.start();},error:fail
 });
}
