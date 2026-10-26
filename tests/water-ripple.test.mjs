import test from 'node:test';
import assert from 'node:assert/strict';
import {waveProgress} from '../site/water-ripple.js';

test('water front moves continuously outward, slowing after impact instead of using constant speed',()=>{
 const positions=Array.from({length:101},(_,i)=>waveProgress(i/100));
 assert.equal(positions[0],0);assert.equal(positions[100],1);
 const steps=positions.slice(1).map((value,i)=>value-positions[i]);
 assert.ok(steps.every(step=>step>0));
 assert.ok(steps.every((step,i)=>i===0||step<steps[i-1]));
 assert.ok(steps[0]>steps.at(-1)*5);
 assert.equal(waveProgress(-.5),0);assert.equal(waveProgress(1.5),1);
});
