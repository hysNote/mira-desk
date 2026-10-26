"""Check all shipped sprite atlases against the accepted still desktop."""
import json
from pathlib import Path
from PIL import Image
import numpy as np
root=Path(__file__).resolve().parents[1];assets=root/'site/assets';out=assets/'carousel'
m=json.loads((out/'motion.json').read_text());assert len(m['styles'])==11
x0,y0,x1,y1=m['crop'];w=m['width'];h=m['height'];report={}
for style in m['styles']:
    atlas=Image.open(out/f'{style}.webp').convert('RGB');assert atlas.size==(w*5,h*5)
    a=np.asarray(atlas,dtype=np.float32);first=a[:h,:w];last=a[4*h:5*h,4*w:5*w]
    base=np.asarray(Image.open(assets/'styles'/f'{style}.webp').convert('RGB'),dtype=np.float32)[y0:y1,x0:x1]
    seam=float(np.mean(np.abs(first-base)));movement=float(np.mean(np.abs(first-last)))
    assert seam<3,(style,seam)
    assert movement>1,(style,movement)
    report[style]={'bytes':(out/f'{style}.webp').stat().st_size,'first_frame_mean_error_255':seam,'motion_mean_difference_255':movement,'dimensions':atlas.size}
(root/'build/carousel-motion/assets-audit.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
