import {ITEMS, EXPERIENCE, LIFE, AWARDS, PLACES, NOTEBOOK_PAGES} from './content.js';
const $ = s => document.querySelector(s);
const layoutVersion=new URLSearchParams(location.search).get('layout');
const sceneAssets=['a','b','c'].includes(layoutVersion)?`layouts/${layoutVersion}/`:'assets/';
$('#desk-image').src=sceneAssets+'scene.webp';
const panel=$('#panel'), content=$('#panel-content'), lightbox=$('#lightbox');
const state={current:null,resumeTab:'all',photos:[],photoSet:[],photoAt:0,pet:0,notePage:0,noteOpening:true};
const esc=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let trigger=null, sceneData=null, hitPixels=null;
const itemById=id=>ITEMS.find(x=>x.id===id);
const availableItems=()=>sceneData?ITEMS.filter(i=>sceneData.keys.includes(i.id)):ITEMS;
const action=(id,text,cls='secondary')=>`<button class="${cls}" data-open="${id}">${text}</button>`;
function jobCard(j){return `<article class="job" id="job-${j.id}"><span class="date">${j.date}</span><h3>${j.title}</h3><p class="role">${j.role}</p><p>${j.summary}</p><div class="metrics">${j.metrics.map(([n,t])=>`<div><b>${n}</b><span>${t}</span></div>`).join('')}</div><details><summary>展开项目与我的贡献</summary><ul>${j.points.map(p=>`<li>${p}</li>`).join('')}</ul>${j.link?`<a class="text-link" target="_blank" rel="noopener noreferrer" href="${j.link.url}">${j.link.text}</a>`:''}</details></article>`;}
function exploration(){return `<p class="lead">离开熟悉的轨道，试着把想法变成自己的生活。</p><div class="timeline"><article><small>2023 · 离开大厂</small><h3>给自己一次重新选择的机会</h3><p>裸辞后开始自由探索，尝试新的职业路径与生活方式。</p></article><article><small>2024 — 2025 · 边尝试，边调整</small><h3>内容、电商、咨询与知识付费</h3><p>从开店、选品、履约到内容表达和课程，把想法放到真实市场里验证。过程中也不断学习、旅行和调整方向。</p></article><article><small>2025 年末起 · 走向 AI 产品</small><h3>把产品经验带回新的领域</h3><p>参与 WorkfxAI，探索 AI 可见度、营销执行与企业服务之间的连接。</p></article></div><p class="small-note">根据 Mira 提供的探索时间线整理。具体转折故事，之后由 Mira 亲自补上。</p>`;}
function resumeBody(){
 const tabs=[['all','全部'],['career','大厂'],['venture','创业'],['explore','探索']];
 return `<div class="tabs" role="tablist" aria-label="履历分类">${tabs.map(([id,t])=>`<button role="tab" id="tab-${id}" aria-controls="resume-body" aria-selected="${state.resumeTab===id}" tabindex="${state.resumeTab===id?0:-1}" data-tab="${id}">${t}</button>`).join('')}</div><div id="resume-body" role="tabpanel" aria-labelledby="tab-${state.resumeTab}">${state.resumeTab==='explore'?exploration():EXPERIENCE.filter(j=>state.resumeTab==='all'||j.group===state.resumeTab).map(jobCard).join('')}${state.resumeTab==='all'?'<div class="inset"><h3>教育经历</h3><p>大连理工大学 · 软件工程</p><p class="small-note">2013.09 — 2017.07</p></div>':''}</div><p class="small-note">履历与成果数字依据 Mira 提供的简历整理。</p>`;
}
function galleryCards(list,type){return `<div class="gallery">${list.map((p,i)=>`<button data-gallery="${type}" data-index="${i}" aria-label="打开照片：${esc(p.title)}"><img src="${esc(p.src)}" alt="${esc(p.title)}" loading="lazy"><strong>${esc(p.title)}</strong></button>`).join('')}</div>`;}
function photosBody(){return `${state.photos.length?`<p class="small-note">本次打开的本机照片，仅在当前页面预览。</p>${galleryCards(state.photos,'photos')}<button class="text-link" id="clear-photos">清空本次预览</button>`:`<div class="empty"><div class="empty-icon" aria-hidden="true">◉</div><h3>照片还在挑选中</h3><p>这里会放我拍摄的作品。<br>先留一个位置，给值得被看见的瞬间。</p></div>`}<div class="actions"><button class="primary" id="upload-photos">从本机预览照片</button><button class="secondary" id="photo-demo">看看相册交互示例</button></div><input class="file-input" id="photo-input" type="file" accept="image/jpeg,image/png,image/webp,image/gif" multiple aria-label="选择本机照片"><p class="small-note">正式摄影作品待补充。预览文件不会上传，刷新页面后清空。交互示例使用建站参考照片，并非摄影作品。</p><p id="upload-status" class="status" role="status"></p>`;}
function aboutBody(){return `<p class="lead">我是 Mira，门月淇。<br>做过大厂产品，也在海外创业。现在，继续在 AI、内容和生活里探索。</p><div class="chips"><span class="chip">大厂产品</span><span class="chip">海外创业</span><span class="chip">AI 内容创作</span></div><p>从去哪儿、字节跳动的产品工作，到悉尼的跨境电商与 AI 创业，我喜欢把一个想法放到真实世界里试一试。</p><p>桌上也留了另一部分的我：拍过的照片、一起生活的猫，以及装着回忆的旋转木马。</p><div class="actions">${action('resume','翻开我的履历 ↗','primary')}${action('life','看看生活片段')}</div><div class="inset"><h3>在其他地方找到我</h3><p>我也在分享自己的实践与探索。</p><p class="small-note">社媒账号与公开联系方式待 Mira 补充。</p></div>`;}
function awardsBody(){return `<p>先把这些值得记住的时刻留在桌上。完整奖项资料正在整理。</p>${AWARDS.map(a=>`<article class="award"><span class="org">${a.org}</span><h3>${a.title}</h3><span class="badge">资料待补充</span><p>${a.note}</p><button class="text-link" data-experience="${a.experience}">了解对应项目 →</button></article>`).join('')}<p class="small-note">桌上的三座奖杯是造型占位，不代表已经确认三个具体奖项。</p>`;}
function lifeBody(){return `<p>这个旋转木马是我之前 3D 打印的。它上面挂着照片，转动时，就像翻到了生活的另一页。</p><p class="small-note">这一版先放入你提供的两张实物参考；正式生活照片与说明后续替换。</p>${galleryCards(LIFE,'life')}`;}
function travelBody(){return `<p>这一页会慢慢收集去过的地方与当地货币。先从简历里能确认的两个生活坐标开始。</p><div class="places">${PLACES.map(p=>`<button class="place" data-place="${p.id}"><span class="currency">${p.currency}</span><strong>${p.name}</strong><small>${p.tag} ↗</small></button>`).join('')}</div><div id="place-detail" aria-live="polite"><p class="small-note">点开一张卡片，看看与那个地方有关的经历。</p></div><div class="inset"><h3>下一张旅行记忆，留给你来补</h3><p class="small-note">完整去过的国家、旅行照片和收藏货币待补充。卡片是入口示意，不代表实物货币收藏。</p></div>`;}
function catBody(){return `<img class="cat-portrait" src="assets/cat.webp" alt="桌面上蜷着休息的小猫占位模型"><p class="greeting" id="cat-greeting" role="status">你好呀，我是陪伴 Mira 很久的小猫。</p><button class="primary" id="pet-cat">轻轻打个招呼</button><p class="small-note">名字和真实外观待补充。这一版先让我在桌上睡一会儿。</p>`;}
function notebookBody(){
 const page=NOTEBOOK_PAGES[state.notePage];
 return `<div class="note-book"><aside class="note-index"><span class="note-small">MIRA’S NOTEBOOK</span><p class="note-hand">边做，边想。</p><nav aria-label="笔记目录">${NOTEBOOK_PAGES.map((p,i)=>`<button data-note-page="${i}" ${i===state.notePage?'aria-current="page"':''}><small>0${i+1}</small>${p.label}<span>↗</span></button>`).join('')}</nav><p class="note-margin">不必等到想清楚，<br>先记下一点点。</p></aside><section class="note-paper" aria-labelledby="note-page-title"><span class="note-small">${state.notePage===0?'IN PROGRESS':'SOMEDAY, MAYBE'}</span><h3 id="note-page-title" tabindex="-1">${page.title}</h3>${page.entries.map(e=>`<article class="note-entry"><span class="note-status">进行中</span><h4>${e.title}</h4><p>${e.body}</p><p class="note-pencil">${e.note}</p></article>`).join('')}${page.prompts?`<div class="note-prompts">${page.prompts.map(p=>`<p><span aria-hidden="true">□</span> ${p}</p>`).join('')}</div>`:''}<p class="note-blank">${page.blank}</p><div class="note-pagination"><button data-note-step="-1" ${state.notePage===0?'disabled':''} aria-label="上一页笔记">← 上一页</button><span role="status">${state.notePage+1} / ${NOTEBOOK_PAGES.length}</span><button data-note-step="1" ${state.notePage===NOTEBOOK_PAGES.length-1?'disabled':''} aria-label="下一页笔记">下一页 →</button></div>${state.noteOpening?'<div class="note-cover" aria-hidden="true"><span>AI<br>随手记</span><small>边做，边想。</small></div>':''}</section></div>`;
}
function turnNotePage(index){
 if(!Number.isInteger(index)||index<0||index>=NOTEBOOK_PAGES.length||index===state.notePage)return;
 state.notePage=index;state.noteOpening=false;content.innerHTML=notebookBody();$('#note-page-title').focus({preventScroll:true});
}
panel.addEventListener('keydown',e=>{if(state.current==='notebook'&&['ArrowLeft','ArrowRight'].includes(e.key)){e.preventDefault();turnNotePage(state.notePage+(e.key==='ArrowRight'?1:-1));}});
const renderers={about:aboutBody,resume:resumeBody,awards:awardsBody,photos:photosBody,life:lifeBody,travel:travelBody,cat:catBody,notebook:notebookBody};
function renderPanel(){
 const it=itemById(state.current);panel.dataset.section=it.id; $('#panel-kicker').textContent=it.kicker; $('#panel-title').textContent=it.title; $('#panel-subtitle').textContent=it.sub; $('#panel-number').textContent=`${it.n} / ${String(availableItems().length).padStart(2,'0')}`;
 content.innerHTML=renderers[it.id]();
 const items=availableItems(),i=items.indexOf(it), prev=items[(i+items.length-1)%items.length],next=items[(i+1)%items.length];
 $('#panel-nav').innerHTML=`<button data-open="${prev.id}">← ${prev.label}</button><button data-open="${next.id}">${next.label} →</button>`;
 panel.scrollTop=0;
}
function openPanel(id){
 if(!itemById(id))return;
 if(!panel.open)trigger=document.activeElement;
 state.current=id; state.resumeTab='all'; state.pet=0;state.notePage=0;state.noteOpening=true; renderPanel();
 if(!panel.open)panel.showModal();
 $('#panel-close').focus({preventScroll:true});
}
function closePanel(){panel.close();trigger?.focus({preventScroll:true});}
$('#panel-close').addEventListener('click',closePanel);
panel.addEventListener('cancel',e=>{e.preventDefault();closePanel();});
function closeOnBackdrop(dialog,close){dialog.addEventListener('click',e=>{if(e.target!==dialog)return;const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)close();});}
closeOnBackdrop(panel,closePanel);closeOnBackdrop(lightbox,()=>lightbox.close());
function showPhoto(){const p=state.photoSet[state.photoAt]; $('#lightbox-image').src=p.src;$('#lightbox-image').alt=p.title;$('#lightbox-title').textContent=p.title;$('#lightbox-caption').textContent=p.caption||'';$('#lightbox-count').textContent=`${state.photoAt+1} / ${state.photoSet.length}`;$('#photo-prev').disabled=state.photoSet.length<2;$('#photo-next').disabled=state.photoSet.length<2;}
function openPhoto(list,index=0){if(!list.length)return;state.photoSet=list;state.photoAt=index;showPhoto();lightbox.showModal();$('#lightbox-close').focus();}
function stepPhoto(step){state.photoAt=(state.photoAt+step+state.photoSet.length)%state.photoSet.length;showPhoto();}
$('#photo-prev').addEventListener('click',()=>stepPhoto(-1));$('#photo-next').addEventListener('click',()=>stepPhoto(1));$('#lightbox-close').addEventListener('click',()=>lightbox.close());
lightbox.addEventListener('keydown',e=>{if(e.key==='ArrowLeft'){e.preventDefault();stepPhoto(-1);}if(e.key==='ArrowRight'){e.preventDefault();stepPhoto(1);}});
document.addEventListener('keydown',e=>{if(e.target.matches('[data-tab]')&&['ArrowLeft','ArrowRight','Home','End'].includes(e.key)){e.preventDefault();let tabs=[...content.querySelectorAll('[data-tab]')],i=tabs.indexOf(e.target);i=e.key==='Home'?0:e.key==='End'?tabs.length-1:(i+(e.key==='ArrowRight'?1:-1)+tabs.length)%tabs.length;state.resumeTab=tabs[i].dataset.tab;content.innerHTML=resumeBody();content.querySelector(`[data-tab="${state.resumeTab}"]`).focus();}});
document.addEventListener('click',e=>{
 const b=e.target.closest('button');if(!b)return;
 if(b.dataset.notePage!==undefined){turnNotePage(Number(b.dataset.notePage));return;}
 if(b.dataset.noteStep){turnNotePage(state.notePage+Number(b.dataset.noteStep));return;}
 if(b.dataset.open){openPanel(b.dataset.open);return;}
 if(b.dataset.tab){state.resumeTab=b.dataset.tab;content.innerHTML=resumeBody();content.querySelector(`[data-tab="${state.resumeTab}"]`).focus({preventScroll:true});return;}
 if(b.dataset.experience){const id=b.dataset.experience;openPanel('resume');const card=$(`#job-${id}`);card.querySelector('details').open=true;card.scrollIntoView({block:'start',behavior:'instant'});return;}
 if(b.dataset.gallery){openPhoto(b.dataset.gallery==='life'?LIFE:state.photos,Number(b.dataset.index));return;}
 if(b.dataset.place){const p=PLACES.find(p=>p.id===b.dataset.place);$('#place-detail').innerHTML=`<article class="inset"><span class="eyebrow">${p.status}</span><h3>${p.title}</h3><p>${p.body}</p>${action('resume','在履历里继续看 →')}</article>`;return;}
 if(b.id==='photo-demo')openPhoto(LIFE.map(p=>({...p,title:'交互示例 · '+p.title,caption:'这是建站参考素材，用于演示照片浏览；并非 Mira 的摄影作品。'})));
 if(b.id==='upload-photos')$('#photo-input').click();
 if(b.id==='clear-photos'){state.photos.forEach(p=>URL.revokeObjectURL(p.src));state.photos=[];content.innerHTML=photosBody();}
 if(b.id==='pet-cat'){const lines=['喵。很高兴认识你。','今天的任务：在这里陪 Mira 工作。','好啦，我要继续晒太阳了。'];$('#cat-greeting').textContent=lines[state.pet++%lines.length];}
});
document.addEventListener('change',async e=>{
 if(e.target.id!=='photo-input')return;
 const status=$('#upload-status');status.textContent='正在打开照片…';let rejected=0;let accepted=0;
 for(const file of [...e.target.files].slice(0,30)){
   if(!['image/jpeg','image/png','image/webp','image/gif'].includes(file.type)||file.size>20*1024*1024){rejected++;continue;}
   const url=URL.createObjectURL(file),img=new Image();img.src=url;
   try{await img.decode();state.photos.push({src:url,title:file.name.replace(/\.[^.]+$/,''),caption:'本机预览 · 未上传，刷新后清空'});accepted++;}catch{URL.revokeObjectURL(url);rejected++;}
 }
 if(state.current==='photos'){content.innerHTML=photosBody();$('#upload-status').textContent=`已打开 ${accepted} 张照片。${rejected?'部分文件格式不支持或超过 20 MB，已跳过。':''}`;}
});
window.addEventListener('pagehide',()=>state.photos.forEach(p=>URL.revokeObjectURL(p.src)));
$('#object-nav').innerHTML=ITEMS.map(i=>`<button data-open="${i.id}"><span>${i.n}</span>${i.label}</button>`).join('');
$('#hint-toggle').addEventListener('click',()=>{const on=$('#hint-toggle').getAttribute('aria-pressed')!=='true';$('#hint-toggle').setAttribute('aria-pressed',String(on));$('#hint-toggle span').textContent=on?'开':'关';$('#pins').classList.toggle('is-hidden',!on);});
// Actual Blender ID pass drives the click regions; HTML pins provide keyboard access.
const pinFractions={about:[.5,.52],resume:[.5,.35],awards:[.52,.42],photos:[.5,.3],life:[.5,.34],travel:[.5,.4],cat:[.5,.4],notebook:[.40,.62]};
async function initScene(){
 try{
  const response=await fetch(sceneAssets+'scene.json');if(!response.ok)throw Error('scene metadata');sceneData=await response.json();
  await $('#desk-image').decode();const hot=new Image();hot.src=sceneAssets+'hot-index.png';await hot.decode();const c=document.createElement('canvas');c.width=sceneData.width;c.height=sceneData.height;const ctx=c.getContext('2d',{willReadFrequently:true});ctx.drawImage(hot,0,0);hitPixels=ctx.getImageData(0,0,c.width,c.height).data;
  $('#object-nav').innerHTML=availableItems().map(i=>`<button data-open="${i.id}"><span>${i.n}</span>${i.label}</button>`).join('');
  $('#pins').innerHTML=availableItems().map(it=>{const [x0,y0,x1,y1]=sceneData.hots[it.id].bbox,[fx,fy]=pinFractions[it.id];return `<button class="pin" data-open="${it.id}" style="left:${(x0+(x1-x0)*fx)/c.width*100}%;top:${(y0+(y1-y0)*fy)/c.height*100}%" aria-label="${it.object}：${it.label}"><i>${it.n}</i><span>${it.label}</span></button>`;}).join('');
  $('#scene-status').hidden=true;document.body.dataset.ready='true';
 }catch(error){$('#scene-status').textContent='桌面画面暂未加载完整。你仍可通过下方入口浏览全部内容。';console.error('Scene load failed',error);}
}
function hitAt(e){if(!hitPixels)return null;const r=$('#scene').getBoundingClientRect(),x=Math.floor((e.clientX-r.left)/r.width*sceneData.width),y=Math.floor((e.clientY-r.top)/r.height*sceneData.height);if(x<0||y<0||x>=sceneData.width||y>=sceneData.height)return null;const index=hitPixels[(y*sceneData.width+x)*4];return index?sceneData.keys[index-1]:null;}
$('#scene').addEventListener('pointermove',e=>{const id=hitAt(e);$('#scene').style.cursor=id?'pointer':'default';document.querySelectorAll('.pin').forEach(p=>p.classList.toggle('is-hover',p.dataset.open===id));});
$('#scene').addEventListener('pointerleave',()=>document.querySelectorAll('.pin').forEach(p=>p.classList.remove('is-hover')));
$('#scene').addEventListener('click',e=>{if(e.target.closest('button'))return;const id=hitAt(e);if(id)openPanel(id);});
initScene();
