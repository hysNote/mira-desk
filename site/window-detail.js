// Painted, dimensional assets for the two refined scenes. All remain behind
// the exact same outdoor ID mask; this never changes the room or its lighting.
const images=new Map(),pending=new Map();
const editions=new Map();
const urls={sunset:'assets/windows/sunset-v2.png',ocean:'assets/windows/ocean-v2.png',whale:'assets/windows/whale-v3.png'};
export async function loadDetailedWindow(id){
 const keys=id==='sunset'?['sunset']:id==='ocean'?['ocean','whale']:[];
 await Promise.all(keys.map(key=>{
  if(images.has(key))return;
  if(!pending.has(key)){
   const image=new Image();image.src=urls[key];
   pending.set(key,image.decode().then(()=>images.set(key,image)).catch(error=>{pending.delete(key);throw error}));
  }
  return pending.get(key);
 }));
}
const seed=n=>{const a=Math.sin(n*43.719+217)*17321.7;return a-Math.floor(a)};
function artwork(key,style){
 const source=images.get(key);
 const cacheKey=key+':'+style;if(editions.has(cacheKey))return editions.get(cacheKey);
 // Deliberately collapse the generated microtexture into broad painted masses.
 // Exterior detail should stay below the desk's detail, including in soft styles.
 const canvas=document.createElement('canvas');canvas.width=key==='whale'?256:288;canvas.height=Math.round(canvas.width*source.naturalHeight/source.naturalWidth);
 const ctx=canvas.getContext('2d',{willReadFrequently:true});
 ctx.filter=key==='whale'?'blur(.85px)':'blur(1.25px)';ctx.drawImage(source,0,0,canvas.width,canvas.height);ctx.filter='none';
 const pixels=ctx.getImageData(0,0,canvas.width,canvas.height),data=pixels.data;
 for(let i=0;i<data.length;i+=4){
  if(data[i+3]<8)continue;
  const l=data[i]*.299+data[i+1]*.587+data[i+2]*.114;
  const q=Math.round(l/255*6)*255/6,f=.55+.45*q/Math.max(l,1);
  for(let ch=0;ch<3;ch++)data[i+ch]=Math.min(255,data[i+ch]*f);
 }
 ctx.putImageData(pixels,0,0);canvas.naturalWidth=canvas.width;canvas.naturalHeight=canvas.height;
 editions.set(cacheKey,canvas);if(editions.size>8)editions.delete(editions.keys().next().value);return canvas;
}
function haze(c,x,y,r,color){const g=c.createRadialGradient(x,y,0,x,y,r);g.addColorStop(0,color);g.addColorStop(1,'transparent');c.fillStyle=g;c.fillRect(x-r,y-r,r*2,r*2);}
function whale(c,x,y,width,time,style,alpha=1,distant=false){
 const image=artwork('whale',style),height=width*image.naturalHeight/image.naturalWidth;
 c.save();c.translate(x,y);c.rotate(-.04+Math.sin(time*.24)*.018);c.globalAlpha=alpha;
 if(distant)c.filter='blur(1.4px) saturate(.6)';
 // Slight, continuous tail flex; the head stays stable and the fine alpha
 // silhouette is preserved. Overlap by half a pixel to avoid strip seams.
 const strips=64,sw=image.naturalWidth/strips,dw=width/strips;
 for(let i=0;i<strips;i++){
  const u=i/(strips-1),tail=Math.max(0,(u-.55)/.45),dy=Math.sin(time*.8-u*2)*tail*tail*width*.008;
  c.drawImage(image,i*sw,0,Math.min(sw+1,image.naturalWidth-i*sw),image.naturalHeight,-width/2+i*dw,-height/2+dy,dw+.5,height);
 }
 c.restore();
}
export function paintDetailedWindow(c,id,time,style){
 if(!images.has(id)||(id==='ocean'&&!images.has('whale')))return false;
 c.save();
 if(id==='sunset'){
  c.fillStyle='#b28b9e';c.fillRect(0,0,1920,1080);
  const image=artwork('sunset',style),sy=image.naturalHeight*.176,sh=image.naturalHeight-sy;
  // A quiet differential drift: nearer upper cloud banks move slightly more
  // than the distant horizon. No repeated icon clouds or decorative stripes.
  for(let y=0;y<610;y+=20){
   const band=Math.min(21,610-y),parallax=Math.sin(time*.045)*(1-y/610)**2*8;
   c.drawImage(image,0,sy+y/610*sh,image.naturalWidth,band/610*sh,350+parallax,-30+y,1590,band);
  }
  haze(c,1500,282,220,`rgba(255,219,161,${.045+Math.sin(time*.19)*.012})`);
  // Pigment wash joins the cloud colors to the desk's subdued painted palette.
  c.globalCompositeOperation='soft-light';c.fillStyle=style==='watercolor'?'#b7a1b126':'#c0abd018';c.fillRect(0,0,1920,600);c.globalCompositeOperation='source-over';
 }else if(id==='ocean'){
  c.fillStyle='#164b70';c.fillRect(0,0,1920,1080);
  const image=artwork('ocean',style);
  c.drawImage(image,565+Math.sin(time*.028)*3,-130,1395,930);
  c.globalCompositeOperation='soft-light';const wash=c.createLinearGradient(0,0,0,620);wash.addColorStop(0,'#a79ac43b');wash.addColorStop(1,'#45406655');c.fillStyle=wash;c.fillRect(0,0,1920,1080);c.globalCompositeOperation='source-over';
  // The nearby whale has its own pace and gentle body pitch, rather than
  // moving the entire underwater view as one flat photograph.
  whale(c,1490-Math.sin(time*.035)*50,315+Math.sin(time*.2)*5,515,time,style,.78);
  // Soft moving light and suspended particles cross in front of the whale.
  c.save();c.globalCompositeOperation='screen';
  for(let i=0;i<3;i++){
   c.save();c.translate(810+i*245+Math.sin(time*.13+i)*24,0);c.rotate(-.30);
   const g=c.createLinearGradient(-28,0,70,0);g.addColorStop(0,'#b9efef00');g.addColorStop(.48,'#c1f3ed0d');g.addColorStop(1,'#b9efef00');c.fillStyle=g;c.fillRect(-28,-100,100,900);c.restore();
  }
  c.restore();
  for(let i=0;i<14;i++){
   const z=seed(i+7),x=645+seed(i)*1250+Math.sin(time*.16+i)*7,y=(seed(i+50)*680-time*(2+z*5)+680)%680;
   c.globalAlpha=.025+z*.06;c.fillStyle='#d9f2ed';c.beginPath();c.arc(x,y,.5+z*1.8,0,Math.PI*2);c.fill();
  }
  c.globalAlpha=1;
 }
 c.restore();return true;
}
