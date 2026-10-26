import test from 'node:test';
import assert from 'node:assert/strict';
import {carrierProgress,createCarouselMotion} from '../site/carousel-motion.js';

function environment({reduced=false,fail=false}={}){
 const draws=[],events={},requests=[],frames=new Map();let next=0,now=0;
 const canvas={hidden:true,style:{},dataset:{},getContext:()=>({drawImage(...args){draws.push(args)},globalAlpha:1})};
 const status={textContent:''},body={dataset:{style:'comic'}};
 globalThis.document={body,querySelector:s=>s==='#carousel-motion'?canvas:status,addEventListener:(name,fn)=>events[name]=fn};
 globalThis.window={addEventListener(){}};
 globalThis.matchMedia=()=>({matches:reduced});
 globalThis.performance={now:()=>now};
 globalThis.requestAnimationFrame=fn=>{frames.set(++next,fn);return next};
 globalThis.cancelAnimationFrame=id=>frames.delete(id);
 globalThis.fetch=async()=>({ok:!fail,json:async()=>({crop:[339,409,578,661],canvas:[1920,1080],width:239,height:252,frames:25,columns:5,duration_ms:2900})});
 globalThis.Image=class{decode(){return new Promise((resolve,reject)=>requests.push({resolve,reject}))}};
 return {canvas,body,requests,draws,events,tick:()=>new Promise(resolve=>setImmediate(resolve)),advance(time){now=time;const callbacks=[...frames.values()];frames.clear();callbacks.forEach(fn=>fn(time));}};
}
test('photo carrier eases in and out without reversing or overshooting',()=>{
 const p=Array.from({length:101},(_,i)=>carrierProgress(i/100));
 assert.equal(p[0],0);assert.equal(p[100],1);
 assert.ok(p.slice(1).every((v,i)=>v>p[i]));
 assert.ok(p[1]<p[51]-p[50]);assert.ok(1-p[99]<p[51]-p[50]);
});
test('one click sequence waits for native motion to finish; rapid clicks share it',async()=>{
 const e=environment(),motion=createCarouselMotion();const promise=motion.play();
 assert.equal(motion.play(),promise);await e.tick();e.requests[0].resolve();await e.tick();
 assert.equal(e.body.dataset.carouselRunning,'playing');assert.equal(e.canvas.hidden,false);
 let finished=false;promise.then(()=>finished=true);e.advance(1450);await e.tick();assert.equal(finished,false);
 e.advance(2900);assert.equal(await promise,true);assert.equal(e.canvas.dataset.frame,'24');assert.equal(motion.running,false);
});
test('cancelling an undecoded animation prevents a late gallery opening',async()=>{
 const e=environment(),motion=createCarouselMotion();const promise=motion.play();await e.tick();
 motion.cancel();assert.equal(await promise,false);e.requests[0].resolve();await e.tick();
 assert.equal(e.canvas.hidden,true);assert.equal(e.draws.length,0);assert.equal(motion.running,false);
});
test('Escape stops an active rotation',async()=>{
 const e=environment(),motion=createCarouselMotion();const promise=motion.play();await e.tick();e.requests[0].resolve();await e.tick();
 e.events.keydown({key:'Escape',preventDefault(){}});assert.equal(await promise,false);e.advance(4000);assert.equal(e.canvas.hidden,true);
});
test('reduced motion and missing assets still let visitors reach the photos',async()=>{
 let e=environment({reduced:true});assert.equal(await createCarouselMotion().play(),true);assert.equal(e.requests.length,0);
 e=environment({fail:true});const old=console.warn;console.warn=()=>{};
 try{assert.equal(await createCarouselMotion().play(),true);assert.equal(e.canvas.hidden,true);}finally{console.warn=old;}
});
