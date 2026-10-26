import test from 'node:test';
import assert from 'node:assert/strict';
import {paintWindow as oldPaint} from './fixtures/window-art-v1.js';
import {paintWindow as newPaint} from '../site/window-art.js';
import {STYLES} from '../site/styles.js';

function drawing(){
 const calls=[];let gradient=0;
 const ctx=new Proxy({}, {
  set(_,key,value){calls.push(['set',key,value]);return true},
  get(_,key){
   return (...args)=>{
    calls.push([key,...args]);
    if(String(key).startsWith('create')){
     const id=gradient++;
     return {id,addColorStop(...stops){calls.push(['stop',id,...stops]);}};
    }
   };
  }
 });
 return {ctx,calls};
}
test('accepted sunset and ocean fallback scenery is unchanged by the weather refinement',()=>{
 for(const scene of ['sunset','ocean'])for(const style of STYLES){
  const before=drawing(),after=drawing();oldPaint(before.ctx,scene,7.25,style.id);newPaint(after.ctx,scene,7.25,style.id);
  assert.equal(JSON.stringify(after.calls),JSON.stringify(before.calls),scene+':'+style.id);
 }
});
test('simplified weather remains deterministic and animated across all desk styles',()=>{
 for(const scene of ['storm','snow','rainbow'])for(const style of STYLES){
  const a=drawing(),b=drawing(),later=drawing();
  newPaint(a.ctx,scene,7.25,style.id);newPaint(b.ctx,scene,7.25,style.id);newPaint(later.ctx,scene,9.25,style.id);
  assert.equal(JSON.stringify(a.calls),JSON.stringify(b.calls),scene+':'+style.id);
  assert.notEqual(JSON.stringify(a.calls),JSON.stringify(later.calls),scene+' must retain motion');
  for(const call of a.calls)for(const arg of call)if(typeof arg==='number')assert.ok(Number.isFinite(arg),scene+' has finite coordinates');
 }
});
test('detailed assets share in-flight decoding and failed downloads can be retried',async()=>{
 const {loadDetailedWindow}=await import('../site/window-detail.js?test=loading');const requests=[];
 globalThis.Image=class{decode(){return new Promise((resolve,reject)=>requests.push({src:this.src,resolve,reject}))}};
 const first=loadDetailedWindow('ocean'),again=loadDetailedWindow('ocean');
 assert.equal(requests.length,2);requests.forEach(r=>r.resolve());await Promise.all([first,again]);
 await loadDetailedWindow('ocean');await loadDetailedWindow('storm');assert.equal(requests.length,2);
 const failed=loadDetailedWindow('sunset');requests[2].reject(Error('offline'));await assert.rejects(failed,/offline/);
 const retry=loadDetailedWindow('sunset');assert.equal(requests.length,4);requests[3].resolve();await retry;
});
