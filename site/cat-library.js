
import * as THREE from 'three';
import {GLTFLoader} from './vendor/three/GLTFLoader.js';
const $=s=>document.querySelector(s),stage=$('#stage'),canvas=$('#cat-canvas');
const candidates={
 bicolor:{file:'bicolor_cat.glb',name:'Bicolor Cat',author:'kenchoo',source:'https://sketchfab.com/3d-models/bicolor-cat-e623a618ca344a8393d7ba4d63ec23cf',label:'轻微呼吸、转头、尾巴动作',loops:1},
 toon:{file:'toon_cat_free.glb',name:'Toon Cat FREE',author:'Omabuarts Studio',source:'https://sketchfab.com/3d-models/toon-cat-free-b2bd1ee7858444bda366110a2d960386',label:'原地走路循环',loops:5}
};
const renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.15;renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;
const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(32,1,.01,100),anchor=new THREE.Group();scene.add(anchor);
scene.add(new THREE.HemisphereLight(0xeaf5ff,0xa28c72,2.1));
const light=new THREE.DirectionalLight(0xffefd9,2.5);light.position.set(-3,5,4);light.castShadow=true;light.shadow.mapSize.set(1024,1024);Object.assign(light.shadow.camera,{left:-4,right:4,top:4,bottom:-4,near:.1,far:20});light.shadow.bias=-.0003;light.shadow.normalBias=.012;scene.add(light);
const floor=new THREE.Mesh(new THREE.PlaneGeometry(20,20),new THREE.ShadowMaterial({opacity:.19}));floor.rotation.x=-Math.PI/2;floor.receiveShadow=true;scene.add(floor);
let mixer,model,clip,config,deskCamera,ready=false,playing=false,t=0,duration=1,close=true,last=performance.now(),ticket=0,dirty=true,originalMaterials=[];
function readout(){
 $('#motion-status').textContent=ready?(playing?config.label:'轻轻摸一下，播放现成动作'):'正在加载…';
 $('#timeline').value=t/duration*1000;$('#time').textContent=t.toFixed(1)+' / '+duration.toFixed(1)+' 秒';
}
function pose(){if(!ready)return;mixer.setTime(Math.min(t,duration-.0001)%clip.duration);dirty=true;readout();}
function play(reset=true){if(!ready||playing)return;if(reset||t>=duration)t=0;playing=true;$('#pet-play').textContent='正在回应你…';$('#pause-play').textContent='暂停';}
function pause(){playing=false;$('#pet-play').textContent='再摸摸它';$('#pause-play').textContent='继续';readout();}
function resize(){const r=stage.getBoundingClientRect();if(!r.width||!r.height)return;renderer.setSize(r.width,r.height,false);camera.aspect=r.width/r.height;camera.updateProjectionMatrix();dirty=true;}
function view(isClose){
 close=isClose;stage.classList.toggle('close-view',close);$('#close-view').setAttribute('aria-pressed',String(close));$('#desk-view').setAttribute('aria-pressed',String(!close));
 if(close){camera.fov=32;camera.position.set(1.65,1.2,2.65);camera.lookAt(0,.45,0);anchor.position.set(0,0,0);anchor.scale.setScalar(1);anchor.rotation.y=0;floor.position.y=-.006;}
 else if(deskCamera){camera.fov=deskCamera.fov;camera.position.fromArray(deskCamera.position);camera.quaternion.fromArray(deskCamera.quaternion);anchor.position.fromArray(deskCamera.cat_position);anchor.scale.setScalar(deskCamera.cat_height);anchor.rotation.y=Math.PI*.35;floor.position.y=deskCamera.cat_position[1]-.005;}
 resize();
}
function coat(){for(const {mesh,material} of originalMaterials){const selected=$('#plain-coat').checked?material.map(m=>m.userData.clay):material;mesh.material=selected.length===1?selected[0]:selected;}dirty=true;$('.clay-label').textContent=$('#plain-coat').checked?'素色看体型 · 暂不制作你家猫的花纹':'原作者配色 · 暂非你家猫的花色';}
function disposeModel(){
 if(!model)return;anchor.remove(model);const textures=new Set(),materials=new Set();
 model.traverse(o=>{if(o.isMesh)o.geometry.dispose();});
 for(const item of originalMaterials)for(const m of item.material){materials.add(m);materials.add(m.userData.clay);for(const value of Object.values(m))if(value?.isTexture)textures.add(value);}
 textures.forEach(t=>t.dispose());materials.forEach(m=>m.dispose());originalMaterials=[];model=null;
}
async function load(name){
 const current=++ticket;pause();ready=false;t=0;$('#timeline').disabled=$('#pet-play').disabled=$('#pause-play').disabled=true;$('#load-error').hidden=true;config=candidates[name]||candidates.bicolor;readout();disposeModel();dirty=true;
 try{
  const gltf=await new GLTFLoader().loadAsync('assets/cat-library/'+config.file);if(current!==ticket)return;
  model=gltf.scene;clip=gltf.animations[0];if(!clip?.duration)throw Error('No author animation');mixer=new THREE.AnimationMixer(model);mixer.clipAction(clip).play();mixer.update(0);model.updateMatrixWorld(true);
  const box=new THREE.Box3().setFromObject(model),size=box.getSize(new THREE.Vector3()),center=box.getCenter(new THREE.Vector3()),scale=1/size.y;
  model.scale.multiplyScalar(scale);model.position.set(-center.x*scale,-box.min.y*scale,-center.z*scale);
  model.traverse(o=>{if(!o.isMesh)return;o.castShadow=true;o.receiveShadow=true;const material=(Array.isArray(o.material)?o.material:[o.material]).map(m=>{const c=m.clone();c.userData.clay=new THREE.MeshStandardMaterial({color:0xb5b8b3,roughness:.77,metalness:0,side:m.side});return c;});o.material=material;originalMaterials.push({mesh:o,material});});
  anchor.add(model);duration=clip.duration*config.loops;ready=true;$('#timeline').disabled=$('#pet-play').disabled=$('#pause-play').disabled=false;$('#pet-play').textContent='摸摸它';$('#source-link').href=config.source;$('#source-link').textContent=config.name+' / '+config.author;$('#clip-description').textContent=config.label;coat();pose();view(close);
 }catch(error){$('#load-error').hidden=false;$('#motion-status').textContent='加载失败';console.error(error);}
}
new ResizeObserver(resize).observe(stage);
$('#pet-play').onclick=()=>play();$('#pet-target').onclick=()=>play();$('#pause-play').onclick=()=>playing?pause():play(false);$('#timeline').oninput=e=>{const fraction=Number(e.target.value)/1000;pause();t=fraction*duration;pose();};
$('#close-view').onclick=()=>view(true);$('#desk-view').onclick=()=>view(false);$('#cat-source').onchange=e=>load(e.target.value);$('#plain-coat').onchange=coat;
let stroke=null,armed=true;
$('#pet-target').addEventListener('pointerenter',e=>{stroke=[e.clientX,e.clientY,performance.now()];armed=true;});
$('#pet-target').addEventListener('pointermove',e=>{if(e.pointerType==='touch'||!stroke||!armed||matchMedia('(prefers-reduced-motion: reduce)').matches)return;if(Math.hypot(e.clientX-stroke[0],e.clientY-stroke[1])>22&&performance.now()-stroke[2]>100){armed=false;play();}});
$('#pet-target').addEventListener('pointerleave',()=>{stroke=null;});
document.addEventListener('visibilitychange',()=>{if(document.hidden)pause();else dirty=true;});document.addEventListener('keydown',e=>{if(e.key==='Escape')pause();});
try{const r=await fetch('assets/cat-library/desk-camera.json');if(!r.ok)throw Error('camera');deskCamera=await r.json();}catch{$('#desk-view').disabled=true;}
const params=new URLSearchParams(location.search);if(params.get('embed')==='1')document.body.classList.add('embedded');const name=params.get('model')==='toon'?'toon':'bicolor';$('#cat-source').value=name;view(true);await load(name);
renderer.setAnimationLoop(now=>{const dt=Math.min((now-last)/1000,.1);last=now;if(document.hidden)return;if(playing&&ready){t+=dt;if(t>=duration){t=0;pause();}pose();}if(dirty){renderer.render(scene,camera);dirty=false;}});
window.addEventListener('pagehide',()=>{renderer.setAnimationLoop(null);disposeModel();renderer.dispose();});

