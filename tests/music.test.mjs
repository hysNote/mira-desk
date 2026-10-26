import test from 'node:test';
import assert from 'node:assert/strict';
import {createMusicMixer,musicForScene} from '../site/music.js';

function setup(){
 let time=0;const frames=new Map(),players=[];let nextFrame=0;
 const mixer=createMusicMixer({now:()=>time,frame:fn=>{frames.set(++nextFrame,fn);return nextFrame;},cancel:id=>frames.delete(id),makeAudio:src=>{
  let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b;});
  const p={src,volume:0,paused:true,play(){this.paused=false;return promise;},pause(){this.paused=true;},removeAttribute(){},load(){},resolve,reject};players.push(p);return p;
 }});
 return {mixer,players,tick(ms){time+=ms;const pending=[...frames.values()];frames.clear();pending.forEach(fn=>fn(time));}};
}
test('nothing autoplays; fixed scene music covers five outdoor scenes',()=>{
 const h=setup();assert.equal(h.players.length,0);h.mixer.select('dream');assert.equal(h.players.length,0);
 assert.equal(musicForScene('sunset'),'bossa');assert.equal(musicForScene('rainbow'),'guitar');
 assert.equal(musicForScene('storm'),'guitar');assert.equal(musicForScene('ocean'),'dream');assert.equal(musicForScene('snow'),'dream');
});
test('changing tracks fades old/new together and releases old voice after two seconds',async()=>{
 const h=setup();let work=h.mixer.start('bossa');h.players[0].resolve();await work;h.tick(2000);assert.equal(h.players[0].volume,.32);
 work=h.mixer.start('guitar');h.players[1].resolve();await work;h.tick(1000);
 assert.equal(h.players[0].volume,.16);assert.equal(h.players[1].volume,.16);
 h.tick(1000);assert.equal(h.players[0].paused,true);assert.equal(h.mixer.getState().voices,1);
 h.mixer.destroy();assert.equal(h.players[1].paused,true);
});
test('rapid changes and stop invalidate pending play so no late music starts',async()=>{
 const h=setup();const a=h.mixer.start('bossa'),b=h.mixer.start('dream');h.players[1].resolve();await b;h.players[0].resolve();await a;
 assert.equal(h.players[0].paused,true);assert.equal(h.mixer.getState().selected,'dream');
 const c=h.mixer.start('guitar');h.mixer.stop();h.players[2].resolve();await c;h.tick(2000);
 assert.equal(h.mixer.getState().voices,0);assert.equal(h.mixer.getState().enabled,false);
});
test('same-track scene change keeps position; playback errors stop cleanly',async()=>{
 const h=setup();let work=h.mixer.start('dream');h.players[0].resolve();await work;
 await h.mixer.select('dream');assert.equal(h.players.length,1);
 await h.mixer.setHidden(true);assert.equal(h.players[0].paused,true);
 await h.mixer.setHidden(false);assert.equal(h.players[0].paused,false);
 work=h.mixer.start('guitar');h.players[1].reject(new Error('media unavailable'));await work;
 assert.equal(h.mixer.getState().enabled,false);assert.equal(h.mixer.getState().voices,0);
});
