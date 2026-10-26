"""Upstream comic foundation, tuned line hierarchy and physical material highlights."""
from pathlib import Path
from upstream_stylize import Ctx, comic, cv2, np, Image
root=Path(__file__).resolve().parents[1]
passes=root/'build/passes'
shape=cv2.imread(str(passes/'albedo.png')).shape
for group in ['screen','rgb','lamp']:
    cv2.imwrite(str(passes/f'light_{group}.exr'),np.zeros(shape,dtype=np.float32))
class MiraCtx(Ctx):
    def lines(self,*args,**kwargs):
        # A fine outline on miniature mouldings; stronger contours on furniture.
        general=super().lines(.9,.35,.20,wobble=.2,vary=False,city=.35)
        fine=super().lines(.35,.18,.12,wobble=.1,vary=False,city=.25)
        mask=cv2.GaussianBlur(self.mask('carousel','laptop key','camera','wallet stitch','earbud').astype(np.float32),(0,0),1.5)
        self.ink=general*(1-mask)+fine*mask
        return self.ink
ctx=MiraCtx(passes)
result=comic(ctx)
beauty=np.asarray(Image.open(root/'site/assets/scene.png').convert('RGB'),dtype=np.float32)/255
# Let physical light describe form. The earlier ink-gated blend removed highlights
# exactly where raised mouldings met their shadows, leaving a flat black contour.
material=ctx.mask('lens','camera','teapot','teacup','wallet','award','star award','crystal prize','round prize').astype(np.float32)
amount=(.65+material*.16)*(1-ctx.ink*.4)
result=result*(1-amount[...,None])+beauty*amount[...,None]
# Pearl needs continuous reflections across the whole assembly, not object-ID lines
# around every bead and curl. Keep only a trace of the printed colour treatment.
pearl=ctx.mask('carousel')
result=np.where(pearl[...,None],beauty*.97+result*.03,result)
mat=ctx.mask('tiger deskmat')
result=np.where(mat[...,None],beauty*.35+ctx.A*.65,result)
# The simplified outdoor painting should keep its blue/green colour, not receive
# the interior comic highlight/glow treatment like a pale illuminated wall.
sky=ctx.mask('sky')
result=np.where(sky[...,None],beauty*.30+ctx.A*.70,result)
collage=ctx.mask('felt board photo collage')
result=np.where(collage[...,None],ctx.A*.80+beauty*.20,result)
decor=ctx.mask('uplighter','plant','bird','mini bin','wallet','pineapple')
result=np.where(decor[...,None],beauty*.78+ctx.A*.22,result)
rug=ctx.mask('room woven rug','room rug flower')
result=np.where(rug[...,None],beauty*.65+ctx.A*.35,result)
# Tiny screen typography and actual photographs should remain legible, without RGB misregistration.
readable=ctx.mask('resume screen','intro screen','carousel hanging photograph','carousel photo caption','journal handwritten cover')
readable=cv2.erode(readable.astype(np.uint8),np.ones((3,3),np.uint8)).astype(bool)
result=np.where(readable[...,None],ctx.A*.82+beauty*.18,result)
Image.fromarray((np.clip(result,0,1)*255).astype(np.uint8)).save(root/'build/comic.png')
print('Refined comic composite complete')
