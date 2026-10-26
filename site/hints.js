// Exact silhouette feedback, inspired by the reference's one-at-a-time hover.
export function createHints(sceneData,pixels,labelOf){
 const canvas=document.querySelector('#hover-outline'),ctx=canvas.getContext('2d'),tip=document.querySelector('#hover-label'),scene=document.querySelector('#scene');
 canvas.width=sceneData.width;canvas.height=sceneData.height;
 const masks=new Map();let last=null;
 function clear(){last=null;ctx.clearRect(0,0,canvas.width,canvas.height);tip.hidden=true}
 function show(id,x,y){
  if(!id||document.querySelector('#hint-toggle').getAttribute('aria-pressed')!=='true'){clear();return}
  if(last!==id){
   const index=sceneData.hots[id]?.index;if(!index){clear();return}
   if(!masks.has(id)){
    if(masks.size>=3)masks.clear();
    const mask=document.createElement('canvas');mask.width=canvas.width;mask.height=canvas.height;const m=mask.getContext('2d'),data=m.createImageData(mask.width,mask.height),w=mask.width,h=mask.height;
    const [x0,y0,x1,y1]=sceneData.hots[id].bbox;
    for(let py=Math.max(3,y0-3);py<=Math.min(h-4,y1+3);py++)for(let px=Math.max(3,x0-3);px<=Math.min(w-4,x1+3);px++){
     const p=py*w+px,inside=pixels[p*4]===index;
     if(inside||[p-3,p+3,p-3*w,p+3*w].some(n=>pixels[n*4]===index)){
      data.data[p*4]=255;data.data[p*4+1]=255;data.data[p*4+2]=255;data.data[p*4+3]=inside?20:190;
     }
    }m.putImageData(data,0,0);m.globalCompositeOperation='source-in';m.fillStyle=getComputedStyle(document.documentElement).getPropertyValue('--style-accent').trim()||'#e6c48a';m.fillRect(0,0,w,h);masks.set(id,mask);
   }
   ctx.clearRect(0,0,canvas.width,canvas.height);ctx.drawImage(masks.get(id),0,0);last=id;
  }
  tip.textContent=labelOf(id);tip.hidden=false;
  tip.style.left=Math.max(8,Math.min(x+16,innerWidth-tip.offsetWidth-12))+'px';tip.style.top=Math.max(8,Math.min(y+18,innerHeight-tip.offsetHeight-12))+'px';
 }
 scene.addEventListener('pointermove',e=>{if(e.pointerType==='touch')clear()});
 document.querySelector('#hint-toggle').addEventListener('click',clear);
 return {show,clear,invalidate(){masks.clear();clear()}};
}
