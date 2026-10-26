export const STYLES=[
 {id:'original',name:'原版 · 珠光日常',accent:'#8aa47a',paper:'#fff8e9',ink:'#263d35'},
 {id:'comic',name:'漫画 · 布鲁克林墨线',accent:'#ffd23f',paper:'#fff3ce',ink:'#171722'},
 {id:'noir',name:'黑白 · 黑色电影',accent:'#a9a7ad',paper:'#efede5',ink:'#111117'},
 {id:'pop',name:'波普 · 彩色网点',accent:'#f32957',paper:'#fff9d8',ink:'#161620'},
 {id:'anime',name:'动画 · 梦幻机甲',accent:'#a48bf1',paper:'#f0e6ff',ink:'#3a2466'},
 {id:'watercolor',name:'水彩 · 柔和纸感',accent:'#9acbc4',paper:'#fffaf0',ink:'#4a4660'},
 {id:'punk',name:'拼贴 · 朋克印刷',accent:'#ff2e88',paper:'#f8f400',ink:'#111014'},
 {id:'neon',name:'霓虹 · 未来夜色',accent:'#36e3ee',paper:'#15182f',ink:'#b6faff'},
 {id:'sketch',name:'素描 · 文艺复兴',accent:'#c49a68',paper:'#e8d5ac',ink:'#3d2616'},
 {id:'pixel',name:'像素 · 复古街机',accent:'#a7f070',paper:'#ffe9b0',ink:'#1a1c2c'},
 {id:'void',name:'墨绘 · 黑白留白',accent:'#ff741f',paper:'#fbfaf6',ink:'#111114'}
];
export async function initStyles({sceneAssets,layoutVersion,transition,onChange}){
 const select=document.querySelector('#style-select'),image=document.querySelector('#desk-image'),status=document.querySelector('#style-status');
 const historical=['a','c'].includes(layoutVersion);
 const choices=historical?STYLES.slice(0,1):STYLES;
 select.innerHTML=choices.map(s=>`<option value="${s.id}">${s.name}</option>`).join('');
 select.disabled=historical;
 if(historical)select.title='A、C 是保留的早期布局；回到主页面可切换全部风格';
 let requested=new URLSearchParams(location.search).get('style'),serial=0;
 if(!requested){try{requested=localStorage.getItem('mira-desk-style')}catch{}}
 let current='original';
 const initial=historical?'original':STYLES.some(s=>s.id===requested)?requested:'comic';
 async function change(id,persist=true){
  const style=choices.find(s=>s.id===id);if(!style)return;
  transition?.cancel();
  const ticket=++serial;select.value=id;select.setAttribute('aria-busy','true');status.textContent='正在切换画风…';
  const src=historical?sceneAssets+'scene.webp':`assets/styles/${id}.webp`;
  try{
   const next=new Image();next.src=src;await next.decode();if(ticket!==serial)return;
   let previous;
   if(persist&&transition){previous=new Image();previous.src=image.src;await previous.decode();if(ticket!==serial)return;}
   image.src=src;document.body.dataset.style=id;current=id;
   document.documentElement.style.setProperty('--style-accent',style.accent);
   document.documentElement.style.setProperty('--control-paper',style.paper);
   document.documentElement.style.setProperty('--control-ink',style.ink);
   document.querySelector('#style-name').textContent=style.name;
   status.textContent='';
   if(persist){try{localStorage.setItem('mira-desk-style',id)}catch{}const url=new URL(location.href);url.searchParams.set('style',id);history.replaceState(null,'',url);}
   onChange?.();
   if(previous)await transition.play(previous,next);
  }catch(error){if(ticket!==serial)return;select.value=current;status.textContent='画风未加载成功，已保留当前画面。';console.error('Style load failed',error);}
  finally{if(ticket===serial)select.removeAttribute('aria-busy');}
 }
 select.addEventListener('change',()=>change(select.value));
 await change(initial,false);
 return {select:change,next(){
  if(historical)return Promise.resolve();
  const index=choices.findIndex(s=>s.id===select.value);
  return change(choices[(index+1)%choices.length].id);
 }};
}
