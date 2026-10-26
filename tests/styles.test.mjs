import test from 'node:test';
import assert from 'node:assert/strict';
import {initStyles} from '../site/styles.js';

function environment(search='?style=comic'){
 const nodes=Object.fromEntries(['style-select','desk-image','style-status','style-name'].map(id=>[id,{value:'',textContent:'',attrs:{},listeners:{},src:'assets/scene.webp',setAttribute(k,v){this.attrs[k]=v},removeAttribute(k){delete this.attrs[k]},addEventListener(k,fn){this.listeners[k]=fn}}]));
 const requests=[],stored=new Map(),body={dataset:{}},url={href:'http://localhost/'+search,search};
 globalThis.document={body,querySelector:s=>nodes[s.slice(1)],documentElement:{style:{setProperty(){}}}};
 globalThis.location=url;globalThis.history={replaceState(a,b,v){url.href=v.href;url.search=v.search}};
 globalThis.localStorage={getItem:k=>stored.get(k),setItem:(k,v)=>stored.set(k,v)};
 globalThis.Image=class{decode(){return new Promise((resolve,reject)=>requests.push({src:this.src,resolve,reject}))}};
 const tick=()=>new Promise(resolve=>setImmediate(resolve));
 return{nodes,body,requests,stored,url,tick,change(id){nodes['style-select'].value=id;nodes['style-select'].listeners.change()}};
}

test('interactive-cat plates use the same style transaction while historical scenes retain their original image',async()=>{
 let e=environment('?style=watercolor'),init=initStyles({sceneAssets:'assets/',imageForStyle:id=>`assets/home-cat/${id}.webp`});
 assert.equal(e.requests[0].src,'assets/home-cat/watercolor.webp');e.requests[0].resolve();await init;
 e=environment('?layout=c');init=initStyles({sceneAssets:'layouts/c/',layoutVersion:'c',imageForStyle:id=>`assets/home-cat/${id}.webp`});
 assert.equal(e.requests[0].src,'layouts/c/scene.webp');e.requests[0].resolve();await init;
});

test('style changes commit only decoded images; latest request wins and failures retain the current scene',async()=>{
 const e=environment();const init=initStyles({sceneAssets:'assets/'});
 assert.equal(e.requests[0].src,'assets/styles/comic.webp');e.requests[0].resolve();await init;
 assert.equal(e.body.dataset.style,'comic');
 e.change('neon');e.change('watercolor');
 assert.equal(e.nodes['desk-image'].src,'assets/styles/comic.webp');
 e.requests[2].resolve();await e.tick();e.requests[1].resolve();await e.tick();
 assert.equal(e.body.dataset.style,'watercolor');assert.equal(e.nodes['style-select'].value,'watercolor');
 assert.equal(e.stored.get('mira-desk-style'),'watercolor');assert.match(e.url.search,/style=watercolor/);
 const oldError=console.error;console.error=()=>{};
 try{e.change('punk');e.requests[3].reject(Error('missing image'));await e.tick();}finally{console.error=oldError}
 assert.equal(e.nodes['style-select'].value,'watercolor');assert.equal(e.nodes['desk-image'].src,'assets/styles/watercolor.webp');
 assert.match(e.nodes['style-status'].textContent,/保留当前画面/);assert.equal(e.nodes['style-select'].attrs['aria-busy'],undefined);
});

test('invalid URL styles cannot become asset paths; historical layouts keep their matching scene',async()=>{
 let e=environment('?style=../../bad');let init=initStyles({sceneAssets:'assets/'});
 assert.equal(e.requests[0].src,'assets/styles/comic.webp');e.requests[0].resolve();await init;
 e=environment('?layout=a&style=neon');init=initStyles({sceneAssets:'layouts/a/',layoutVersion:'a'});
 assert.equal(e.requests[0].src,'layouts/a/scene.webp');e.requests[0].resolve();await init;
 assert.equal(e.body.dataset.style,'original');assert.equal(e.nodes['style-select'].disabled,true);
});

test('a stored preference is restored when no style is explicitly linked',async()=>{
 const e=environment('');e.stored.set('mira-desk-style','sketch');const init=initStyles({sceneAssets:'assets/'});
 assert.equal(e.requests[0].src,'assets/styles/sketch.webp');e.requests[0].resolve();await init;
 assert.equal(e.body.dataset.style,'sketch');
});

test('late window preparation cannot overwrite the newest complete style and window pair',async()=>{
 const e=environment(),pending=[],committed=[];
 const prepareStyle=id=>new Promise(resolve=>pending.push({id,resolve:()=>resolve(()=>committed.push(id))}));
 const init=initStyles({sceneAssets:'assets/',prepareStyle});e.requests[0].resolve();await e.tick();pending[0].resolve();await init;
 e.change('anime');e.requests[1].resolve();await e.tick();
 e.change('pixel');e.requests[2].resolve();await e.tick();
 assert.equal(e.body.dataset.style,'comic');
 pending[2].resolve();await e.tick();pending[1].resolve();await e.tick();
 assert.deepEqual(committed,['comic','pixel']);assert.equal(e.body.dataset.style,'pixel');
});

test('bell cycles from the dropdown selection, wraps, and advances rapid presses without stale commits',async()=>{
 const e=environment('?style=void');const init=initStyles({sceneAssets:'assets/'});
 e.requests[0].resolve();const controller=await init;
 const wrapped=controller.next();assert.equal(e.requests[1].src,'assets/styles/original.webp');
 e.requests[1].resolve();await wrapped;assert.equal(e.body.dataset.style,'original');
 e.change('watercolor');e.requests[2].resolve();await e.tick();
 const first=controller.next(),second=controller.next();
 assert.equal(e.requests[3].src,'assets/styles/punk.webp');assert.equal(e.requests[4].src,'assets/styles/neon.webp');
 e.requests[4].resolve();await second;e.requests[3].resolve();await first;
 assert.equal(e.body.dataset.style,'neon');assert.equal(e.nodes['style-select'].value,'neon');
 assert.equal(e.stored.get('mira-desk-style'),'neon');
});

test('historical layouts cannot cycle into a style using a different hit map',async()=>{
 const e=environment('?layout=a');const init=initStyles({sceneAssets:'layouts/a/',layoutVersion:'a'});
 e.requests[0].resolve();const controller=await init;await controller.next();
 assert.equal(e.requests.length,1);assert.equal(e.body.dataset.style,'original');
});

test('water transition receives the window scenery in both old and new style frames',async()=>{
 const e=environment('?style=comic'),composed=[],played=[];
 const init=initStyles({sceneAssets:'assets/',transition:{cancel(){},play(a,b){played.push([a,b])}},composeScene(image,style){const frame={src:image.src,style,window:'ocean'};composed.push(frame);return frame;}});
 e.requests[0].resolve();await init;e.change('anime');e.requests[1].resolve();await e.tick();e.requests[2].resolve();await e.tick();
 assert.deepEqual(composed.map(f=>f.style),['comic','anime']);assert.equal(played[0][0].window,'ocean');assert.equal(played[0][1].window,'ocean');
});

test('a new style cancels the running transition and only the latest decoded image commits',async()=>{
 const e=environment();let complete=null,cancelled=0;const played=[];
 const transition={cancel(){if(complete){cancelled++;complete();complete=null}},play(a,b){played.push([a.src,b.src]);return new Promise(resolve=>{complete=resolve})}};
 const init=initStyles({sceneAssets:'assets/',transition});e.requests[0].resolve();await init;
 e.change('neon');e.requests[1].resolve();await e.tick();e.requests[2].resolve();await e.tick();
 assert.equal(e.body.dataset.style,'neon');assert.equal(played.length,1);
 e.change('watercolor');assert.equal(cancelled,1);e.requests[3].resolve();await e.tick();e.requests[4].resolve();await e.tick();
 assert.equal(e.body.dataset.style,'watercolor');assert.deepEqual(played[1],['assets/styles/neon.webp','assets/styles/watercolor.webp']);
 complete();complete=null;await e.tick();assert.equal(e.nodes['style-select'].attrs['aria-busy'],undefined);
});
