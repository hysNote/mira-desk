import * as THREE from 'three';
import {GLTFLoader} from './vendor/three/GLTFLoader.js';
import {createCatPlayback,createCatHoverGate,phaseAt} from './cat-local-motion.js';

// Same authored GLB and clip as the approved close-up, at the native room camera.
export async function createHomeCat(){
 const host=document.querySelector('#scene'),canvas=document.querySelector('#home-cat');
 const renderer=new THREE.WebGLRenderer({canvas,alpha:true,antialias:true,preserveDrawingBuffer:true});
 renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.15;
 renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;
 const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(47.52,16/9,.01,100);
 const anchor=new THREE.Group();scene.add(anchor);
 scene.add(new THREE.HemisphereLight(0xe9f3ff,0x9a917f,2));
 const key=new THREE.DirectionalLight(0xfff2df,2.5);key.position.set(-2,4,3);key.castShadow=true;
 key.shadow.mapSize.set(1024,1024);Object.assign(key.shadow.camera,{left:-3,right:3,top:3,bottom:-3,near:.1,far:15});
 key.shadow.bias=-.0002;key.shadow.normalBias=.005;scene.add(key);
 const ground=new THREE.Mesh(new THREE.PlaneGeometry(8,8),new THREE.ShadowMaterial({opacity:.20}));
 ground.rotation.x=-Math.PI/2;ground.receiveShadow=true;scene.add(ground);
 let gltf,cam;
 try{[gltf,cam]=await Promise.all([
  new GLTFLoader().loadAsync('assets/mira-block-cat/mira-block-cat.glb'),
  fetch('assets/cat-library/desk-camera.json').then(r=>{if(!r.ok)throw Error('Cat camera');return r.json();})
 ]);}catch(e){renderer.dispose();throw e;}
 const cat=gltf.scene,clip=gltf.animations[0];
 if(!clip||Math.abs(clip.duration-8)>.05){renderer.dispose();throw Error('Cat clip missing');}
 cat.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;}});anchor.add(cat);
 anchor.position.fromArray(cam.cat_position);anchor.scale.setScalar(.60);anchor.rotation.y=-.12;
 ground.position.y=cam.cat_position[1]-.002;
 camera.fov=cam.fov;camera.position.fromArray(cam.position);camera.quaternion.fromArray(cam.quaternion);camera.updateProjectionMatrix();
 const mixer=new THREE.AnimationMixer(cat),action=mixer.clipAction(clip);
 action.setLoop(THREE.LoopOnce,1);action.clampWhenFinished=true;action.play();
 const playback=createCatPlayback(8),ray=new THREE.Raycaster(),pointer=new THREE.Vector2();
 const target=new THREE.WebGLRenderTarget(1,1,{depthBuffer:true});
 const post=new THREE.Scene(),postCamera=new THREE.OrthographicCamera(-1,1,1,-1,0,1);
 const uniforms={frame:{value:target.texture},texel:{value:new THREE.Vector2(1,1)},mode:{value:0}};
 const shader=new THREE.ShaderMaterial({uniforms,transparent:true,depthTest:false,depthWrite:false,
  vertexShader:'varying vec2 uvp;void main(){uvp=uv;gl_Position=vec4(position.xy,0.,1.);}',
  fragmentShader:`uniform sampler2D frame;uniform vec2 texel;uniform float mode;varying vec2 uvp;
   void main(){vec2 uv=uvp;if(mode==6.)uv=(floor(uv/(texel*3.))+0.5)*texel*3.;
    vec4 p=texture2D(frame,uv);vec3 c=p.rgb;float a=p.a;
    float lum=dot(c,vec3(.299,.587,.114));
    if(mode==1.)c*=max(.012,floor(lum*8.+.5)/8.)/max(lum,.0001);
    if(mode==2.)c=vec3(lum);
    if(mode==3.)c=mix(c,vec3(.56,.57,.62),.16);
    if(mode==4.)c=mix(c,vec3(.10,.25,.40),.35)+vec3(.035,0.,.06);
    if(mode==5.)c=vec3(lum)*vec3(1.12,.91,.68);
    if(mode==6.)c*=max(.012,floor(lum*6.+.5)/6.)/max(lum,.0001);
    if(mode==7.)c=vec3(smoothstep(.02,.24,lum));
    if(mode==1.||mode==2.||mode==5.||mode==7.){
     float edge=0.;for(int i=-1;i<=1;i++){for(int j=-1;j<=1;j++){
      float other=texture2D(frame,uv+vec2(float(i),float(j))*texel*1.2).a;
      edge=max(edge,step(.8,a)*(1.-step(.8,other)));}}
     c=mix(c,vec3(.012,.014,.022),edge*.8);
    }
    gl_FragColor=vec4(c,a);
    #include <tonemapping_fragment>
    #include <colorspace_fragment>
   }`});
 post.add(new THREE.Mesh(new THREE.PlaneGeometry(2,2),shader));
 const hoverGate=createCatHoverGate();
 let active=false,disposed=false,dirty=true,raf=0,last=0;
 function treatment(id){return {comic:1,pop:1,punk:1,anime:1,noir:2,watercolor:3,neon:4,sketch:5,pixel:6,void:7}[id]||0;}
 function render(){
  if(disposed)return;renderer.setRenderTarget(target);renderer.setClearColor(0,0);renderer.clear();renderer.render(scene,camera);
  renderer.setRenderTarget(null);renderer.clear();renderer.render(post,postCamera);dirty=false;
 }
 function pose(){action.paused=false;mixer.setTime(playback.time);cat.updateMatrixWorld(true);cat.traverse(o=>{if(o.isSkinnedMesh)o.computeBoundingSphere();});
  canvas.dataset.phase=phaseAt(playback.time);canvas.dataset.time=playback.time.toFixed(2);dirty=true;
 }
 function resize(){const r=host.getBoundingClientRect(),w=Math.min(1920,Math.round(r.width*Math.min(devicePixelRatio,1.5))),h=Math.round(w*9/16);
  if(!w)return;renderer.setSize(w,h,false);target.setSize(w,h);uniforms.texel.value.set(1/w,1/h);dirty=true;if(active)render();}
 function reset(){playback.seek(0);pose();}
 function blocked(){return document.hidden||document.querySelector('dialog[open]')||document.body.dataset.transitionRunning;}
 function tick(now){raf=0;if(disposed||!active||blocked()){last=0;return;}
  const dt=last?Math.min((now-last)/1000,.1):0;last=now;
  if(playback.update(dt))pose();if(dirty)render();
  if(playback.playing)raf=requestAnimationFrame(tick);else last=0;
 }
 function resume(){if(!raf)raf=requestAnimationFrame(tick);}
 function touch(){if(!active||blocked()||!playback.touch())return false;pose();resume();return true;}
 function hit(event){if(!active||blocked())return false;const r=host.getBoundingClientRect();pointer.set((event.clientX-r.left)/r.width*2-1,1-(event.clientY-r.top)/r.height*2);
  ray.setFromCamera(pointer,camera);return ray.intersectObject(cat,true).length>0;}
 function hover(event,force=false){const inside=(force&&active&&!blocked())||hit(event);if(hoverGate.enter(inside,event.pointerType!=='touch'&&!matchMedia('(prefers-reduced-motion: reduce)').matches))touch();return inside;}
 host.addEventListener('pointerleave',()=>hoverGate.leave());
 document.addEventListener('visibilitychange',()=>{last=0;if(!document.hidden)resume();});
 const observer=new MutationObserver(()=>{if(!blocked()){last=0;resume();}});
 observer.observe(document.body,{attributes:true,attributeFilter:['data-transition-running']});
 for(const d of document.querySelectorAll('dialog'))observer.observe(d,{attributes:true,attributeFilter:['open']});
 const ro=new ResizeObserver(resize);ro.observe(host);pose();resize();
 window.addEventListener('pagehide',()=>{disposed=true;cancelAnimationFrame(raf);observer.disconnect();ro.disconnect();mixer.stopAllAction();target.dispose();shader.dispose();ground.geometry.dispose();ground.material.dispose();post.children[0].geometry.dispose();const mats=new Set();cat.traverse(o=>{o.geometry?.dispose();if(o.material)(Array.isArray(o.material)?o.material:[o.material]).forEach(m=>mats.add(m));});mats.forEach(m=>m.dispose());renderer.dispose();});
 return {
  hit,hover,touch,get active(){return active;},
  setStyle(id){uniforms.mode.value=treatment(id);active=true;canvas.hidden=false;reset();render();},
  compose(image,id){
   if(!active)return image;const before=uniforms.mode.value;uniforms.mode.value=treatment(id);render();
   const result=document.createElement('canvas');result.width=result.naturalWidth=1920;result.height=result.naturalHeight=1080;
   const ctx=result.getContext('2d');ctx.drawImage(image,0,0,1920,1080);ctx.drawImage(canvas,0,0,1920,1080);
   uniforms.mode.value=before;render();return result;
  }
 };
}
