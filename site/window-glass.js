// One quiet translucent pane treatment, applied before the outdoor ID mask.
// Window frames, furniture and all indoor pixels remain crisp and untouched.
export function windowGlassStyle(scene,style){
 const mono=['noir','void','sketch'].includes(style),night=style==='neon';
 const paneColors={sunset:'#e5d9d1',ocean:'#cad9dd',rainbow:'#dce4df',storm:'#bacbd1',snow:'#e0e7e8'};
 const color=mono?'#d1d0cb':night?'#91a7c1':paneColors[scene]||'#cad9dd';
 const tone=style==='noir'?'grayscale(1)':style==='void'?'grayscale(1) brightness(1.08)':style==='sketch'?'sepia(.45)':'saturate(.56)';
 return {color,filter:`${tone} contrast(.76) brightness(1.06) blur(4.5px)`,wash:night?.17:.23};
}
export function paintWindowGlass(ctx,scene,style){
 const {color,wash}=windowGlassStyle(scene,style);
 ctx.save();ctx.fillStyle=color;ctx.globalAlpha=wash;ctx.fillRect(0,0,1920,1080);ctx.globalAlpha=1;
 // Moisture is denser around the pane edges, thinner through the middle.
 const veil=ctx.createRadialGradient(1390,270,100,1390,270,830);
 veil.addColorStop(0,color+'00');veil.addColorStop(.52,color+'12');veil.addColorStop(1,color+'55');
 ctx.fillStyle=veil;ctx.fillRect(0,0,1920,1080);
 const sheen=ctx.createLinearGradient(820,0,1200,170);
 sheen.addColorStop(0,'#ffffff00');sheen.addColorStop(.48,'#ffffff09');sheen.addColorStop(1,'#ffffff00');ctx.fillStyle=sheen;ctx.fillRect(600,0,1320,650);
 ctx.restore();
}
