import * as THREE from 'three';
import {GLTFLoader} from './vendor/three/GLTFLoader.js';
import {createCatPlayback,phaseAt} from './cat-local-motion.js';
const $=s=>document.querySelector(s),stage=$('#stage'),canvas=$('#cat-canvas');
const params=new URLSearchParams(location.search);
if(params.get('embed')==='1')document.body.classList.add('embedded');
const renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.outputColorSpace=THREE.SRGBColorSpace;
renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.15;
renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;
const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(32,1,.01,100),anchor=new THREE.Group();scene.add(anchor);
scene.add(new THREE.HemisphereLight(0xe9f3ff,0x9a917f,2));
const light=new THREE.DirectionalLight(0xfff2df,2.5);light.position.set(2,4,3);light.castShadow=true;
light.shadow.mapSize.set(1024,1024);Object.assign(light.shadow.camera,{left:-3,right:3,top:3,bottom:-3,near:.1,far:15});light.shadow.bias=-.0002;light.shadow.normalBias=.008;scene.add(light);
const ground=new THREE.Mesh(new THREE.PlaneGeometry(20,20),new THREE.ShadowMaterial({opacity:.22}));ground.rotation.x=-Math.PI/2;ground.position.y=-.002;ground.receiveShadow=true;scene.add(ground);
let cat,mixer,clip,action,deskCamera,ready=false,dirty=true,close=true,last=performance.now(),disposed=false;
const playback=createCatPlayback(8),ray=new THREE.Raycaster(),pointer=new THREE.Vector2();
const labels={rest:'窝着休息 · 摸摸我',rise:'醒了，慢慢坐起来',groom:'舔舔爪子，停一小会儿',settle:'好了，继续窝着'};
function status(){
 const phase=phaseAt(playback.time);
 $('#motion-status').textContent=labels[phase]+(!playback.playing&&playback.time>0?' · 已暂停':'');
 $('#time').textContent=playback.time.toFixed(1)+' / 8.0 秒';$('#timeline').value=playback.time/8*1000;
 stage.dataset.playing=String(playback.playing);$('#pet-play').textContent=playback.playing?'正在舔毛…':'摸摸它';
 $('#pause-play').textContent=playback.playing?'暂停':'继续';
 document.querySelectorAll('[data-phase]').forEach(el=>el.dataset.active=String(el.dataset.phase===phase));
}
function pose(){if(!ready)return;action.paused=false;mixer.setTime(playback.time);cat.updateMatrixWorld(true);cat.traverse(o=>{if(o.isSkinnedMesh)o.computeBoundingSphere();});dirty=true;status();}
function touch(){if(ready&&playback.touch())pose();}
function resize(){const r=stage.getBoundingClientRect();if(!r.width||!r.height)return;renderer.setSize(r.width,r.height,false);camera.aspect=r.width/r.height;camera.updateProjectionMatrix();dirty=true;}
function view(isClose){
 close=isClose;stage.classList.toggle('close-view',close);stage.classList.toggle('desk',!close);
 $('#close-view').setAttribute('aria-pressed',String(close));$('#desk-view').setAttribute('aria-pressed',String(!close));
 if(close){camera.fov=32;camera.position.set(1.9,1,1.6);camera.lookAt(0,.40,0);anchor.position.set(0,0,0);anchor.scale.setScalar(1);anchor.rotation.y=0;ground.position.y=-.002;}
 else if(deskCamera){camera.fov=deskCamera.fov;camera.position.fromArray(deskCamera.position);camera.quaternion.fromArray(deskCamera.quaternion);anchor.position.fromArray(deskCamera.cat_position);anchor.scale.setScalar(.60);anchor.rotation.y=-.12;ground.position.y=deskCamera.cat_position[1]-.002;}
 resize();
}
function hit(e){if(!ready)return false;const r=canvas.getBoundingClientRect();pointer.set((e.clientX-r.left)/r.width*2-1,1-(e.clientY-r.top)/r.height*2);ray.setFromCamera(pointer,camera);return ray.intersectObject(cat,true).length>0;}
let stroke=null,armed=true;
canvas.addEventListener('pointermove',e=>{
 const over=hit(e);stage.dataset.hit=String(over);
 if(!over){stroke=null;armed=true;return;}
 if(!stroke)stroke=[e.clientX,e.clientY,performance.now()];
 if(armed&&e.pointerType!=='touch'&&!matchMedia('(prefers-reduced-motion: reduce)').matches&&Math.hypot(e.clientX-stroke[0],e.clientY-stroke[1])>12&&performance.now()-stroke[2]>100){armed=false;touch();}
});
canvas.addEventListener('pointerleave',()=>{stroke=null;armed=true;stage.dataset.hit='false';});
canvas.addEventListener('click',e=>{if(hit(e))touch();});
$('#pet-play').onclick=touch;
$('#pause-play').onclick=()=>{if(playback.playing)playback.pause();else playback.resume();status();};
$('#timeline').oninput=e=>{playback.seek(Number(e.target.value)/1000*8);pose();};
$('#close-view').onclick=()=>view(true);$('#desk-view').onclick=()=>view(false);
new ResizeObserver(resize).observe(stage);
document.addEventListener('visibilitychange',()=>{if(document.hidden){playback.pause();if(ready)status();}else dirty=true;});
document.addEventListener('keydown',e=>{if(e.key==='Escape'){playback.pause();if(ready)status();}});
function release(){if(disposed)return;disposed=true;renderer.setAnimationLoop(null);mixer?.stopAllAction();if(cat){mixer?.uncacheRoot(cat);const mats=new Set();cat.traverse(o=>{o.geometry?.dispose();if(o.material)(Array.isArray(o.material)?o.material:[o.material]).forEach(m=>mats.add(m));});mats.forEach(m=>m.dispose());}ground.geometry.dispose();ground.material.dispose();renderer.dispose();}
window.addEventListener('pagehide',release);
view(true);
try{
 const [gltf,cam]=await Promise.all([new GLTFLoader().loadAsync('assets/mira-block-cat/mira-block-cat.glb'),fetch('assets/cat-library/desk-camera.json').then(r=>{if(!r.ok)throw Error('camera');return r.json();})]);
 if(!disposed){cat=gltf.scene;clip=gltf.animations[0];if(!clip||Math.abs(clip.duration-8)>.05)throw Error('Invalid cat animation duration');deskCamera=cam;cat.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;}});anchor.add(cat);mixer=new THREE.AnimationMixer(cat);action=mixer.clipAction(clip);action.setLoop(THREE.LoopOnce,1);action.clampWhenFinished=true;action.play();ready=true;$('#pet-play').disabled=$('#pause-play').disabled=$('#timeline').disabled=false;pose();view(params.get('view')!=='desk');}
}catch(err){$('#load-error').hidden=false;$('#motion-status').textContent='加载失败';console.error(err);}
renderer.setAnimationLoop(now=>{const dt=Math.min(.1,(now-last)/1000);last=now;if(document.hidden||disposed)return;if(playback.update(dt))pose();if(dirty){renderer.render(scene,camera);dirty=false;}});
