"""Apply only the removed cat/shadow delta to the eleven preserved treatments."""
import json,shutil,sys
from styles import DeskCtx,ROOT,RENDER,STYLES,np,cv2,Image,hexc
from upstream_stylize import Ctx,comic
cv2.setNumThreads(2)
work=ROOT/'build/home-cat/work';work.mkdir(exist_ok=True)
out=ROOT/'site/assets/home-cat';out.mkdir(exist_ok=True)
source=ROOT/'build/home-cat';x0,y0,x1,y1=json.loads((source/'crop.json').read_text());w=x1-x0;h=y1-y0
names=['albedo.png','id.png','normal.png','depth.png','light_sun.exr','light_sky.exr']
for n in ['scene.json','emit.png','light_screen.exr','light_rgb.exr','light_lamp.exr']:shutil.copyfile(ROOT/'build/passes'/n,work/n)
for n in names:
    full=cv2.imread(str(ROOT/'build/passes'/n),cv2.IMREAD_UNCHANGED);patch=cv2.imread(str(source/n),cv2.IMREAD_UNCHANGED)
    assert patch.shape[:2]==(h,w),(n,patch.shape,(h,w))
    full[y0:y1,x0:x1]=patch;cv2.imwrite(str(work/n),full)
yy,xx=np.mgrid[:h,:w];feather=np.clip(np.minimum.reduce([xx,yy,w-1-xx,h-1-yy])/16,0,1)[...,None]
def styled(style,path):
    c=DeskCtx(path)
    if style=='noir':c.A[c.city]=hexc('#182138')
    if style=='neon':c.E[c.mask('uplighter')]*=.35;c.L['lamp']*=.35
    result=RENDER[style](c)
    if style=='void':result=np.where(c.mask('pineapple pen cup')[...,None],result*hexc('#ff741f'),result)
    return np.clip(result,0,1)[y0:y1,x0:x1]
class OriginalCtx(Ctx):
    def lines(self,*args,**kwargs):
        general=super().lines(.9,.35,.20,wobble=.2,vary=False,city=.35)
        fine=super().lines(.35,.18,.12,wobble=.1,vary=False,city=.25)
        mask=cv2.GaussianBlur(self.mask('carousel','laptop key','camera','wallet stitch','earbud').astype(np.float32),(0,0),1.5)
        self.ink=general*(1-mask)+fine*mask
        return self.ink
def original(path,clean=False):
    c=OriginalCtx(path);result=comic(c)
    beauty=np.asarray(Image.open(ROOT/'site/assets/scene.png').convert('RGB'),dtype=np.float32)/255
    if clean:beauty[y0:y1,x0:x1]=np.asarray(Image.open(source/'beauty.png').convert('RGB'),dtype=np.float32)/255
    material=c.mask('lens','camera','teapot','teacup','wallet','award','star award','crystal prize','round prize').astype(np.float32)
    amount=(.65+material*.16)*(1-c.ink*.4)
    result=result*(1-amount[...,None])+beauty*amount[...,None]
    result=np.where(c.mask('carousel')[...,None],beauty*.97+result*.03,result)
    for prefixes,a,b in [(('tiger deskmat',),.35,.65),(('sky',),.30,.70),(('felt board photo collage',),.20,.80),(('uplighter','plant','bird','mini bin','wallet','pineapple'),.78,.22),(('room woven rug','room rug flower'),.65,.35)]:
        result=np.where(c.mask(*prefixes)[...,None],beauty*a+c.A*b,result)
    readable=cv2.erode(c.mask('resume screen','intro screen','carousel hanging photograph','carousel photo caption','journal handwritten cover').astype(np.uint8),np.ones((3,3),np.uint8)).astype(bool)
    result=np.where(readable[...,None],c.A*.82+beauty*.18,result)
    return np.clip(result,0,1)[y0:y1,x0:x1]
for style in (['original'] if '--original-only' in sys.argv else ['original']+STYLES):
    accepted=Image.open(ROOT/'site/assets/styles'/f'{style}.webp').convert('RGB')
    base=np.asarray(accepted,dtype=np.float32)[y0:y1,x0:x1]/255
    if style=='original':
        before=original(ROOT/'build/passes')
        after=original(work,True)
    else:before=styled(style,ROOT/'build/passes');after=styled(style,work)
    patch=np.clip(base+(after-before)*feather,0,1)
    accepted.paste(Image.fromarray(np.rint(patch*255).astype('uint8')),(x0,y0))
    accepted.save(out/f'{style}.webp',lossless=True)
    print('CLEAN_STYLE',style,flush=True)
(out/'manifest.json').write_text(json.dumps({'crop':[x0,y0,x1,y1],'size':[1920,1080],'styles':['original']+STYLES,'preserved':'../styles/'},indent=2))
