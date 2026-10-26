"""Repack completed styled frames without rerendering the room."""
import json
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[1];motion=root/'build/carousel-motion';out=root/'site/assets/carousel'
m=json.loads((out/'motion.json').read_text());w=m['width'];h=m['height']
for style in m['styles']:
    atlas=Image.new('RGB',(w*5,h*5))
    for frame in range(m['frames']):atlas.paste(Image.open(motion/f'{frame:02d}'/f'{style}.png'),((frame%5)*w,(frame//5)*h))
    atlas.save(out/f'{style}.webp',lossless=True,quality=80)
    print('PACKED',style,flush=True)
