// Deterministic vector scenery, animated behind a Blender-derived aperture.
import {paintDetailedWindow} from './window-detail.js';
export const WINDOW_SCENES=[
 {id:'original',name:'原来的窗外',style:null},
 {id:'sunset',name:'落日与彩霞',style:'watercolor'},
 {id:'storm',name:'狂风暴雨',style:'noir'},
 {id:'snow',name:'白雪纷飞',style:'void'},
 {id:'rainbow',name:'雨后的大彩虹',style:'pop'},
 {id:'ocean',name:'海底 · 鲸游梦境',style:'anime'}
];
export const validWindow=id=>WINDOW_SCENES.some(s=>s.id===id)?id:'original';
const TAU=Math.PI*2;
const rnd=n=>{const v=Math.sin(n*127.1+311.7)*43758.5453;return v-Math.floor(v)};
function ellipse(c,x,y,rx,ry,fill,angle=0){c.beginPath();c.ellipse(x,y,rx,ry,angle,0,TAU);c.fillStyle=fill;c.fill();}
function gradient(c,colors){const g=c.createLinearGradient(0,0,0,600);colors.forEach((v,i)=>g.addColorStop(i/(colors.length-1),v));c.fillStyle=g;c.fillRect(0,0,1920,1080);}
function glow(c,x,y,r,color){const g=c.createRadialGradient(x,y,0,x,y,r);g.addColorStop(0,color);g.addColorStop(1,'transparent');c.fillStyle=g;c.fillRect(x-r,y-r,r*2,r*2);}
function cloud(c,x,y,s,color,seed,soft){
 c.save();c.translate(x,y);c.scale(s,s);c.fillStyle=color;
 if(soft){c.shadowColor=color;c.shadowBlur=18;c.filter='blur(3px)';}
 c.beginPath();c.moveTo(-180,10);c.bezierCurveTo(-200,-20,-115,-40,-90,-22);c.bezierCurveTo(-65,-80,15,-74,39,-30);c.bezierCurveTo(90,-67,141,-30,137,-9);c.bezierCurveTo(210,-15,212,27,157,30);c.bezierCurveTo(75,48,-104,38,-180,10);c.fill();c.restore();
}
function ridge(c,y,color,seed,scale=1){c.fillStyle=color;c.beginPath();c.moveTo(400,1080);for(let x=400;x<2001;x+=24)c.lineTo(x,y+Math.sin(x*.004+seed)*37*scale+Math.sin(x*.011+seed)*15*scale);c.lineTo(2000,1080);c.fill();}
function tree(c,x,y,size,wind,color,seed,snow=false){
 c.save();c.translate(x,y);c.scale(size,size);c.strokeStyle=color;c.fillStyle=color;c.lineCap='round';
 c.beginPath();c.moveTo(0,40);c.bezierCurveTo(7,-75,wind*.35,-230,wind,-360);c.lineWidth=12;c.stroke();
 for(let i=0;i<9;i++){
  const side=i%2?1:-1,by=-95-i*27,bx=wind*(-by/360)**2,endx=bx+side*(100-i*5)+wind*.28,endy=by-60;
  c.beginPath();c.moveTo(bx,by);c.quadraticCurveTo(endx*.7,by-30,endx,endy);c.lineWidth=5-i*.32;c.stroke();
  for(let j=0;j<6;j++){
   const a=j/5,px=bx+(endx-bx)*a,py=by+(endy-by)*a;
   ellipse(c,px+side*14,py-12,25+ rnd(seed+i*8+j)*11,10,color,-.55*side+wind*.002);
   if(snow){c.strokeStyle='#f0f7f7';c.lineWidth=4;c.beginPath();c.moveTo(px-13,py-17);c.lineTo(px+16,py-21);c.stroke();c.strokeStyle=color;}
  }
 }
 c.restore();
}
function pine(c,x,y,s,color){c.save();c.translate(x,y);c.scale(s,s);c.fillStyle=color;c.beginPath();c.moveTo(0,-180);for(let i=0;i<5;i++){c.lineTo(24+i*12,-145+i*30);c.lineTo(12+i*8,-145+i*30);}c.lineTo(6,12);c.lineTo(-6,12);for(let i=4;i>=0;i--){c.lineTo(-12-i*8,-145+i*30);c.lineTo(-24-i*12,-145+i*30);}c.closePath();c.fill();c.restore();}
// Broad canopy masses read as trees through glass without individual leaf detail.
function mistTree(c,x,y,s,wind,color){
 c.save();c.translate(x,y);c.scale(s,s);c.strokeStyle=color;c.lineWidth=10;c.lineCap='round';
 c.beginPath();c.moveTo(0,30);c.bezierCurveTo(4,-75,wind*.5,-190,wind,-315);c.stroke();
 for(let i=0;i<5;i++){
  const side=i%2?1:-1,yy=-100-i*45,xx=wind*(-yy/315)**2;
  ellipse(c,xx+side*27+wind*.2,yy,76-i*8,35,color,side*.2+wind*.003);
 }
 c.restore();
}
function whale(c,x,y,s,t,neon){
 c.save();c.translate(x,y);c.rotate(-.055+Math.sin(t*.24)*.028);c.scale(s,s);
 const body=c.createLinearGradient(0,-70,0,65);body.addColorStop(0,neon?'#2c85bf':'#4b7798');body.addColorStop(.55,neon?'#3ebaca':'#6ca1b6');body.addColorStop(1,'#bed9da');
 c.fillStyle=body;c.strokeStyle=neon?'#79f3ef':'#aeced8';c.lineWidth=1.5;
 c.beginPath();c.moveTo(-245,0);c.bezierCurveTo(-235,-65,-139,-100,-25,-64);c.bezierCurveTo(70,-35,115,-2,171,-15);c.bezierCurveTo(193,-49,227,-57,252,-42);c.bezierCurveTo(237,-20,205,-4,181,4);c.bezierCurveTo(202,14,226,30,235,48);c.bezierCurveTo(196,59,173,29,163,15);c.bezierCurveTo(85,54,-25,84,-155,64);c.bezierCurveTo(-215,55,-252,28,-245,0);c.closePath();c.fill();c.stroke();
 c.fillStyle='#93beca';c.beginPath();c.moveTo(-111,36);c.bezierCurveTo(-90,62,-46,119,9,126);c.bezierCurveTo(0,83,-28,48,-48,36);c.fill();
 c.fillStyle='#3e718b';c.beginPath();c.moveTo(-5,-55);c.quadraticCurveTo(15,-91,32,-45);c.fill();
 c.strokeStyle='#d2e3de66';c.lineWidth=1.4;
 for(let i=0;i<9;i++){c.beginPath();c.moveTo(-231+i*7,15+i*3);c.quadraticCurveTo(-171+i*8,65,-67+i*8,59-i*1.2);c.stroke();}
 c.strokeStyle='#365e78';c.beginPath();c.moveTo(-235,17);c.quadraticCurveTo(-202,32,-164,23);c.stroke();
 ellipse(c,-174,4,4,4,'#182e48');ellipse(c,-175,3,1,1,'#efffff');
 for(let i=0;i<24;i++)ellipse(c,-180+rnd(i)*270,-43+rnd(i+90)*42,1.5,1,'#d5e8ea55');
 c.restore();
}
export function paintWindow(c,scene,time,style='watercolor'){
 if(['sunset','ocean'].includes(scene)&&paintDetailedWindow(c,scene,time,style))return;
 const t=time,soft=['watercolor','original','anime'].includes(style),ink=['comic','punk','pop'].includes(style),neon=style==='neon';
 c.save();c.clearRect(0,0,1920,1080);
 if(scene==='sunset'){
  gradient(c,['#76649c','#c98ca9','#f5bd9b','#ffe5ad']);
  glow(c,1455,268,360,'#ffdaa177');ellipse(c,1455,270,65,65,'#fff1c5');
  for(let i=0;i<12;i++){const x=530+rnd(i+1)*1510+Math.sin(t*.028+i)*22,y=20+rnd(i+12)*210;cloud(c,x,y,.65+rnd(i+31)*1.1,i%3===0?'#e8a8b5aa':i%3===1?'#927caa77':'#f8c2baaa',i,soft);}
  for(let i=0;i<7;i++){c.strokeStyle=i%2?'#ffd5b6aa':'#eaa0a4aa';c.lineWidth=7+rnd(i)*9;c.beginPath();c.ellipse(1440+i*13,285+i*17,210-i*17,5,0,.05,Math.PI*.98);c.stroke();}
  ridge(c,435,'#ad91ad',2,.7);ridge(c,470,'#7e819a',7,.65);ridge(c,510,'#626a82',1,.7);
  for(let i=0;i<4;i++){const x=1140+i*43+Math.sin(t*.12)*15,y=170+Math.sin(i*2)*13;c.strokeStyle='#605a77';c.lineWidth=2;c.beginPath();c.moveTo(x-7,y-2);c.quadraticCurveTo(x-3,y-7,x,y);c.quadraticCurveTo(x+3,y-6,x+8,y-2);c.stroke();}
 }else if(scene==='storm'){
  gradient(c,['#657983','#819398','#a3afac','#b8c0b4']);
  for(let i=0;i<6;i++)cloud(c,450+((rnd(i)*1800+t*(7+i%3))%1800),20+rnd(i+30)*170,1.5+rnd(i+22),'#536c7948',i,true);
  ridge(c,407,'#829698',9,.65);ridge(c,470,'#6d8587',2,.6);
  const gust=24+Math.sin(t*1.5)*15+Math.sin(t*2.8)*8;
  mistTree(c,1655,585,1.35,gust,'#536f76');mistTree(c,1900,560,1.15,gust*1.3,'#647f83');mistTree(c,665,495,1.05,gust*.6,'#71888d');
  // A few broad, translucent rain streaks preserve the wind direction, not visual noise.
  for(let i=0;i<85;i++){const z=rnd(i+4),speed=220+z*160,x=500+(rnd(i)*1600+t*speed*.6)%1600,y=(rnd(i+50)*750+t*speed)%740-80;c.lineWidth=2+z*2;c.strokeStyle=`rgba(221,235,237,${.12+z*.18})`;c.beginPath();c.moveTo(x,y);c.lineTo(x+18,y+40+z*20);c.stroke();}
 }else if(scene==='snow'){
  gradient(c,['#a8bbc9','#d5e1e8','#eef2ed','#f5f5e9']);
  glow(c,1460,160,150,'#fffbe677');ridge(c,385,'#becdd3',1,.55);
  for(let i=0;i<10;i++)pine(c,650+i*145,405+rnd(i)*35,.5+rnd(i+20)*.35,'#b1c2c9');
  ridge(c,455,'#edf1ec',4,.4);mistTree(c,1890,520,1.05,Math.sin(t*.35)*3,'#a3b8bf');
  for(let i=0;i<75;i++){const z=rnd(i+15),x=570+(rnd(i)*1400+Math.sin(t*.35+i)*14+t*(4+z*9))%1450,y=(rnd(i+72)*660+t*(10+z*28))%650-40;ellipse(c,x,y,2+z*4,2+z*4,`rgba(255,255,252,${.22+z*.43})`);}
 }else if(scene==='rainbow'){
  gradient(c,['#a2c4d3','#c7dcd9','#e4e7d1','#eee6d0']);
  glow(c,1650,95,230,'#fff4d044');
  const colors=['#e87e88','#efa777','#f6d983','#b5d39c','#91c7cc','#a0b3d9','#c4a6d5'];
  c.save();c.filter='blur(6px)';
  for(let i=0;i<7;i++){c.strokeStyle=colors[i];c.lineWidth=21;c.globalAlpha=.53;c.beginPath();c.arc(1450,510,440-i*16,Math.PI,TAU);c.stroke();}c.restore();
  ridge(c,430,'#acc8ba',6,.65);ridge(c,487,'#94b4a8',9,.5);
  cloud(c,965+Math.sin(t*.04)*12,370,1.1,'#eceee2',1,true);cloud(c,1905+Math.sin(t*.05)*10,330,1.25,'#ecefe5',2,true);
  cloud(c,960+Math.sin(t*.025)*16,85,1,'#f4f4e8aa',4,true);cloud(c,1700,25,1.2,'#f4f7ea88',8,true);
 }else if(scene==='ocean'){
  gradient(c,neon?['#182c65','#134e83','#116e8b','#073d64']:['#598da6','#3e85a4','#317792','#235673']);
  for(let i=0;i<7;i++){const x=890+i*170+Math.sin(t*.12+i)*20,g=c.createLinearGradient(x,0,x+140,700);g.addColorStop(0,'#d4fff72d');g.addColorStop(1,'#b1f8ed00');c.fillStyle=g;c.beginPath();c.moveTo(x,0);c.lineTo(x+25,0);c.lineTo(x+280,710);c.lineTo(x+50,710);c.fill();}
  // A distant companion adds scale; the main whale drifts gently behind mullions.
  c.globalAlpha=.22;whale(c,1770-Math.sin(t*.035)*50,330,.42,t+2,neon);c.globalAlpha=1;
  whale(c,1480-Math.sin(t*.07)*105,265+Math.sin(t*.31)*12,.91,t,neon);
  for(let i=0;i<28;i++){const x=730+((rnd(i)*1300+t*9)%1350),y=350+Math.sin(i)*50+Math.sin(t*.5+i)*3;c.fillStyle='#a5d8d36a';c.beginPath();c.ellipse(x,y,6,2.4,0,0,TAU);c.fill();c.beginPath();c.moveTo(x+5,y);c.lineTo(x+10,y-4);c.lineTo(x+10,y+4);c.fill();}
  for(let i=0;i<64;i++){const x=620+rnd(i)*1300+Math.sin(t*.2+i)*8,y=(rnd(i+90)*750-t*(3+rnd(i)*9)+750)%750;ellipse(c,x,y,.7+rnd(i+20)*2,.7+rnd(i+20)*2,'#d2f3ed55');}
  for(let i=0;i<10;i++){const x=1700+i*27;c.strokeStyle=i%2?'#214e65aa':'#2a6876bb';c.lineWidth=8;c.beginPath();c.moveTo(x,700);c.bezierCurveTo(x-45,580,x+35+Math.sin(t*.6+i)*18,490,x+Math.sin(t*.6+i)*25,430+rnd(i)*100);c.stroke();}
 }
 c.restore();
}
