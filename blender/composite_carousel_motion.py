"""Match native carrier animation to the existing eleven desktop treatments."""
import json,shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from styles import DeskCtx,ROOT,RENDER,STYLES,np,cv2,Image,hexc
cv2.setNumThreads(1)
motion=ROOT/'build/carousel-motion';work=motion/'work';work.mkdir(exist_ok=True)
out=ROOT/'site/assets/carousel';out.mkdir(exist_ok=True)
meta=json.loads((motion/'manifest.json').read_text());x0,y0,x1,y1=meta['crop'];w=x1-x0;h=y1-y0
names=['albedo.png','id.png','normal.png','depth.png','light_sun.exr','light_sky.exr']
base={n:cv2.imread(str(ROOT/'build/passes'/n),cv2.IMREAD_UNCHANGED) for n in names}
for n in ['scene.json','emit.png','light_screen.exr','light_rgb.exr','light_lamp.exr']:
    shutil.copyfile(ROOT/'build/passes'/n,work/n)
styles=['original']+STYLES
static={s:np.asarray(Image.open(ROOT/'site/assets/styles'/f'{s}.webp').convert('RGB'),dtype=np.float32)[y0:y1,x0:x1]/255 for s in styles}
yy,xx=np.mgrid[:h,:w];feather=np.clip(np.minimum.reduce([xx,yy,w-1-xx,h-1-yy])/12,0,1)[...,None]
reference={}
def render_style(style):
    if style=='original':
        result=np.asarray(Image.open(motion/f'{frame:02d}'/'beauty.png').convert('RGB'),dtype=np.float32)/255
    else:
        c=DeskCtx(work)
        if style=='noir':c.A[c.city]=hexc('#182138')
        if style=='neon':c.E[c.mask('uplighter')]*=.35;c.L['lamp']*=.35
        result=RENDER[style](c)
        if style=='void':result=np.where(c.mask('pineapple pen cup')[...,None],result*hexc('#ff741f'),result)
        result=np.clip(result,0,1)[y0:y1,x0:x1]
    if frame==0:reference[style]=result.copy()
    result=np.clip(static[style]+(result-reference[style])*feather,0,1)
    Image.fromarray(np.rint(result*255).astype('uint8')).save(motion/f'{frame:02d}'/f'{style}.png')
with ThreadPoolExecutor(max_workers=2) as pool:
    for frame in range(meta['frames']):
        directory=motion/f'{frame:02d}'
        assert (directory/'ready').exists(),directory
        for n,b in base.items():
            a=b.copy();patch=cv2.imread(str(directory/n),cv2.IMREAD_UNCHANGED)
            assert patch.shape[:2]==(h,w),(n,patch.shape)
            a[y0:y1,x0:x1]=patch;cv2.imwrite(str(work/n),a)
        list(pool.map(render_style,styles))
        print('COMPOSITE_FRAME',frame,flush=True)
for style in styles:
    atlas=Image.new('RGB',(w*5,h*5))
    for frame in range(meta['frames']):atlas.paste(Image.open(motion/f'{frame:02d}'/f'{style}.png'),((frame%5)*w,(frame//5)*h))
    atlas.save(out/f'{style}.webp',lossless=True,quality=80)
meta.update({'columns':5,'width':w,'height':h,'styles':styles})
(out/'motion.json').write_text(json.dumps(meta,indent=2))
print('CAROUSEL_ATLASES_READY',flush=True)
