import test from 'node:test';
import assert from 'node:assert/strict';
import {createCatPlayback,createCatHoverGate,phaseAt} from '../site/cat-local-motion.js';
import fs from 'node:fs';
test('homepage hover plays once per entry, never loops under a stationary mouse, and respects reduced motion',()=>{
 const gate=createCatHoverGate(),p=createCatPlayback();
 if(gate.enter(true))p.touch();p.update(9);
 assert.equal(p.playing,false);assert.equal(gate.enter(true),false);
 gate.enter(false);assert.equal(gate.enter(true),true);
 gate.leave();assert.equal(gate.enter(true,false),false);
 gate.leave();assert.equal(gate.enter(true),true);
});
test('petting starts once; more strokes do not restart or queue the cat',()=>{
 const p=createCatPlayback();assert.equal(p.time,0);assert.equal(p.playing,false);
 assert.equal(p.touch(),true);p.update(3.6);assert.equal(phaseAt(p.time),'groom');
 assert.equal(p.touch(),false);assert.equal(p.time,3.6);
 p.update(4.5);assert.equal(p.time,0);assert.equal(p.playing,false);
 p.update(20);assert.equal(p.time,0);
});
test('pause and scrubbing preserve pose; completion returns to its exact rest',()=>{
 const p=createCatPlayback();p.touch();p.update(2);p.pause();p.update(2);assert.equal(p.time,2);
 p.seek(6.7);assert.equal(phaseAt(p.time),'settle');p.resume();p.update(1.4);
 assert.equal(p.time,0);assert.equal(phaseAt(p.time),'rest');
});
test('local model has a single eight-second clip with matching start and end transforms',()=>{
 const b=fs.readFileSync(new URL('../site/assets/mira-block-cat/mira-block-cat.glb',import.meta.url));
 const len=b.readUInt32LE(12),g=JSON.parse(b.subarray(20,20+len).toString());
 const bin=20+len+8;assert.equal(g.animations.length,1);assert.equal(g.skins.length,1);
 const sizes={SCALAR:1,VEC3:3,VEC4:4};
 function values(i){const a=g.accessors[i],v=g.bufferViews[a.bufferView];assert.equal(a.componentType,5126);const width=sizes[a.type],out=[];
  for(let n=0;n<a.count;n++){const row=[];for(let j=0;j<width;j++)row.push(b.readFloatLE(bin+(v.byteOffset||0)+(a.byteOffset||0)+n*(v.byteStride||width*4)+j*4));out.push(row);}return out;
 }
 for(const sampler of g.animations[0].samplers){const times=values(sampler.input),rows=values(sampler.output);assert.equal(times[0][0],0);assert.equal(times.at(-1)[0],8);for(let j=0;j<rows[0].length;j++)assert.ok(Math.abs(rows[0][j]-rows.at(-1)[j])<.0001);}
});
