// Art-directed dispersing water wave: fast impact, slowing travel, fading wake.
export const waveProgress=t=>Math.log1p(6*Math.max(0,Math.min(1,t)))/Math.log(7);
const VERT=`attribute vec2 p;varying vec2 uv;void main(){uv=vec2((p.x+1.0)*.5,(1.0-p.y)*.5);gl_Position=vec4(p,0.,1.);}`;
const FRAG=`precision highp float;
varying vec2 uv;
uniform sampler2D beforeImage,afterImage;
uniform vec2 size,origin;
uniform float progress,travel;
void main(){
 if(progress<=0.0){gl_FragColor=texture2D(beforeImage,uv);return;}
 if(progress>=1.0){gl_FragColor=texture2D(afterImage,uv);return;}
 vec2 delta=(uv-origin)*size;
 float distance=length(delta);
 vec2 direction=delta/max(distance,1.0);
 vec2 farCorner=max(origin,1.0-origin)*size;
 float scale=size.x/1920.0;
 float radius=travel*(length(farCorner)+250.0*scale);
 float q=(distance-radius)/scale;
 // A short wave train behind the leading wave, rather than shaking the room.
 float packet=exp(-pow((q+68.0)/100.0,2.0))*(1.0-smoothstep(-4.0,30.0,q));
 float life=smoothstep(0.0,.055,progress)*(1.0-smoothstep(.76,1.0,progress));
 float damping=exp(-1.15*progress)*life;
 float wave=sin(q/12.5)*packet*damping;
 vec2 displacement=direction*(8.0*scale*wave)/size;
 vec2 sampleUV=clamp(uv+displacement,vec2(.0001),vec2(.9999));
 float reveal=1.0-smoothstep(-22.0,26.0,q);
 vec3 color=mix(texture2D(beforeImage,sampleUV).rgb,texture2D(afterImage,sampleUV).rgb,reveal);
 // Subtle light/dark facets follow the water slope, with no solid ring stroke.
 float slope=cos(q/12.5)*packet*damping;
 color+=slope*.025*(.65+.35*dot(direction,normalize(vec2(-.6,-.8))));
 gl_FragColor=vec4(clamp(color,0.0,1.0),1.0);
}`;

export function createWaterRipple(){
 const surface=document.createElement('canvas');
 const gl=surface.getContext('webgl',{alpha:false,antialias:false,depth:false,preserveDrawingBuffer:true});
 if(!gl)return null;
 const program=gl.createProgram();
 const compile=(type,source)=>{const shader=gl.createShader(type);gl.shaderSource(shader,source);gl.compileShader(shader);if(!gl.getShaderParameter(shader,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(shader));gl.attachShader(program,shader);return shader};
 const shaders=[compile(gl.VERTEX_SHADER,VERT),compile(gl.FRAGMENT_SHADER,FRAG)];
 gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(program));
 shaders.forEach(s=>gl.deleteShader(s));gl.useProgram(program);
 const buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,1,1]),gl.STATIC_DRAW);
 const position=gl.getAttribLocation(program,'p');gl.enableVertexAttribArray(position);gl.vertexAttribPointer(position,2,gl.FLOAT,false,0,0);
 const uniforms=Object.fromEntries(['beforeImage','afterImage','size','origin','progress','travel'].map(name=>[name,gl.getUniformLocation(program,name)]));
 const textures=[gl.createTexture(),gl.createTexture()];
 textures.forEach((texture,i)=>{gl.activeTexture(gl.TEXTURE0+i);gl.bindTexture(gl.TEXTURE_2D,texture);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE)});
 gl.uniform1i(uniforms.beforeImage,0);gl.uniform1i(uniforms.afterImage,1);
 gl.uniform2f(uniforms.origin,1195/1920,538/1080);
 return {
  prepare(before,after){
   surface.width=before.naturalWidth;surface.height=before.naturalHeight;
   gl.viewport(0,0,surface.width,surface.height);gl.uniform2f(uniforms.size,surface.width,surface.height);
   [before,after].forEach((image,i)=>{gl.activeTexture(gl.TEXTURE0+i);gl.bindTexture(gl.TEXTURE_2D,textures[i]);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,image)});
  },
  draw(ctx,t){
   if(gl.isContextLost())return false;
   gl.uniform1f(uniforms.progress,t);gl.uniform1f(uniforms.travel,waveProgress(t));
   gl.drawArrays(gl.TRIANGLE_STRIP,0,4);ctx.drawImage(surface,0,0);return true;
  }
 };
}
