import test from 'node:test';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {readFile,access} from 'node:fs/promises';
import {ITEMS,EXPERIENCE,AWARDS,LIFE,PLACES} from '../site/content.js';
import {STYLES} from '../site/styles.js';
const root=new URL('../',import.meta.url);

test('eleven styles exist and ten rendered treatments share the scene dimensions',async()=>{
 assert.equal(STYLES.length,11);assert.equal(new Set(STYLES.map(s=>s.id)).size,11);
 const audit=JSON.parse(await readFile(new URL('tests/fixtures/style-audit.json',root)));
 for(const s of STYLES){await access(new URL(`site/assets/styles/${s.id}.webp`,root));if(s.id==='original')continue;
  assert.deepEqual(audit[s.id].size,[1920,1080]);
  for(const key of ['wall_pixels','floor_pixels','window_pixels'])assert.ok(audit[s.id][key]>10000,s.id+': '+key);
 }
});
test('the pre-style B image is preserved byte for byte',async()=>{

 const retained=await readFile(new URL('site/preserved-b/assets/scene.webp',root));
 assert.equal(crypto.createHash('sha256').update(retained).digest('hex'),'946f5d8ab5d220b751c93f92731d0b16b76a59b323e6de9c3e636ba02751b7bf');
});

test('selected B has all entries; earlier layout studies preserve their original entries',async()=>{
 for(const variant of ['a','b','c']){
  const base=`site/layouts/${variant}/`;
  const scene=JSON.parse(await readFile(new URL(base+'scene.json',root)));
  assert.deepEqual(scene.keys,[...ITEMS.filter(i=>variant==='b'||i.id!=='notebook').map(i=>i.id),...(variant==='b'?['style']:[])]);
  assert.deepEqual([scene.width,scene.height],[1920,1080]);
  for(const key of scene.keys)assert.ok(scene.hots[key].pixels>250,variant+': '+key);
  for(const file of ['scene.webp','hot-index.png','homepage.png'])await access(new URL(base+file,root));
 }
});
test('every advertised interactive object has a visible Blender hotspot',async()=>{
 const s=JSON.parse(await readFile(new URL('site/assets/scene.json',root)));
 assert.deepEqual(new Set(s.keys),new Set([...ITEMS.map(i=>i.id),'style']));
 assert.ok(s.hots.style.pixels>250,'bell has a visible click region');
 for(const i of ITEMS){const h=s.hots[i.id];assert.ok(h.pixels>250,i.id);const[x0,y0,x1,y1]=h.bbox;assert.ok(x0>=0&&y0>=0&&x1<s.width&&y1<s.height,i.id);assert.ok(h.center[0]>=x0&&h.center[0]<=x1&&h.center[1]>=y0&&h.center[1]<=y1);}
});
test('award links resolve to supplied career records',()=>{
 for(const a of AWARDS)assert.ok(EXPERIENCE.some(j=>j.id===a.experience));
 assert.equal(EXPERIENCE.filter(j=>j.group==='career').length,2);assert.equal(EXPERIENCE.filter(j=>j.group==='venture').length,2);
});
test('all gallery and render assets exist',async()=>{
 for(const a of ['scene.webp','hot-index.png','cat.webp',...LIFE.map(p=>p.src.replace('assets/',''))])await access(new URL('site/assets/'+a,root));
});
test('no original author services or private phone number in public source',async()=>{
 for(const file of ['site/app.js','site/content.js','site/index.html']){const t=await readFile(new URL(file,root),'utf8');assert.doesNotMatch(t,/evanlin-api|jiaedwin|JOURNAL_PASSWORD/);assert.doesNotMatch(t,/\b1[3-9]\d{9}\b/);}
 assert.deepEqual(PLACES.map(p=>p.id),['cn','au']);
});
test('static site local URLs exist and external project URL uses HTTPS',async()=>{
 const html=await readFile(new URL('site/index.html',root),'utf8');
 for(const [,url] of html.matchAll(/(?:src|href)="([^"]+)"/g)){if(url==='./'||/^(https?:|#)/.test(url))continue;await access(new URL('site/'+url,root));}
 for(const j of EXPERIENCE)if(j.link)assert.equal(new URL(j.link.url).protocol,'https:');
});
