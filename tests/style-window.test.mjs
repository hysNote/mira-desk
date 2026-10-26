import test from 'node:test';
import assert from 'node:assert/strict';
import {STYLES} from '../site/styles.js';
import {STYLE_WINDOWS,windowForStyle} from '../site/style-window.js';
import {WINDOW_SCENES} from '../site/window-art.js';
test('each style has one valid fixed window and all five scenes remain represented',()=>{
 assert.deepEqual(Object.keys(STYLE_WINDOWS).sort(),STYLES.map(s=>s.id).sort());
 for(const s of STYLES)assert.ok(WINDOW_SCENES.some(w=>w.id===windowForStyle(s.id)&&w.id!=='original'));
 assert.equal(new Set(Object.values(STYLE_WINDOWS)).size,5);
 assert.equal(windowForStyle('pixel'),'rainbow');assert.equal(windowForStyle('void'),'snow');
});
