import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import {WINDOW_SCENES,validWindow} from '../site/window-art.js';
import {STYLES} from '../site/styles.js';
test('five window presets use available styles, and unknown window URLs keep the original',()=>{
 assert.deepEqual(WINDOW_SCENES.map(s=>s.id),['original','sunset','storm','snow','rainbow','ocean']);
 for(const s of WINDOW_SCENES.slice(1))assert.ok(STYLES.some(style=>style.id===s.style));
 for(const value of [null,'','../../other','storm?x=1'])assert.equal(validWindow(value),'original');
 assert.equal(validWindow('ocean'),'ocean');
});
test('accepted pre-window website is preserved byte for byte; desk style images and hotspots are untouched',()=>{
 const manifest=JSON.parse(fs.readFileSync(new URL('./fixtures/before-window-scenes.json',import.meta.url)));
 for(const [file,hash] of Object.entries(manifest)){
  const digest=crypto.createHash('sha256').update(fs.readFileSync(new URL('../site/preserved-window/'+file,import.meta.url))).digest('hex');
  assert.equal(digest,hash,file);
  if(file.startsWith('assets/')||file.startsWith('layouts/'))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(new URL('../site/'+file,import.meta.url))).digest('hex'),hash,file);
 }
});
test('outdoor aperture has meaningful area and never overlaps foreground IDs',()=>{
 const mask=JSON.parse(fs.readFileSync(new URL('../site/assets/windows/aperture.json',import.meta.url)));
 assert.equal(mask.foreground_overwrite_pixels,0);assert.ok(mask.pixels>400000);assert.deepEqual(mask.canvas,[1920,1080]);
});
