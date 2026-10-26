"""Pack the physically shaded edition independently of the style compositor."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[1];motion=root/'build/carousel-motion';out=root/'site/assets/carousel';out.mkdir(exist_ok=True)
m=json.loads((motion/'manifest.json').read_text());x0,y0,x1,y1=m['crop'];w=x1-x0;h=y1-y0
base=np.asarray(Image.open(root/'site/assets/styles/original.webp').convert('RGB'),dtype=np.float32)[y0:y1,x0:x1]
ref=np.asarray(Image.open(motion/'00/beauty.png').convert('RGB'),dtype=np.float32)
yy,xx=np.mgrid[:h,:w];feather=np.clip(np.minimum.reduce([xx,yy,w-1-xx,h-1-yy])/12,0,1)[...,None]
atlas=Image.new('RGB',(w*5,h*5))
for f in range(m['frames']):
    pixels=np.asarray(Image.open(motion/f'{f:02d}'/'beauty.png').convert('RGB'),dtype=np.float32)
    frame=Image.fromarray(np.rint(np.clip(base+(pixels-ref)*feather,0,255)).astype('uint8'))
    atlas.paste(frame,((f%5)*w,(f//5)*h))
atlas.save(out/'original.webp',lossless=True,quality=80)
m.update({'columns':5,'width':w,'height':h,'styles':['original']})
(out/'motion.json').write_text(json.dumps(m,indent=2))
