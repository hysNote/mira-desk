"""Adapt all ten upstream styles to Mira's semantic objects, not a flat image filter."""
from pathlib import Path
import json
from upstream_stylize import Ctx,RENDER,STYLES,np,cv2,Image,hexc,luma,blur,mix
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'site/assets/styles';OUT.mkdir(exist_ok=True)

class DeskCtx(Ctx):
    def lines(self,*args,**kwargs):
        general=super().lines(*args,**kwargs)
        # The small red button and golden arches disappear under furniture-scale
        # ink. Keep a miniature-scale contour around the whole bell assembly.
        fine=super().lines(.42,.18,.08,wobble=0,vary=False,city=0)
        bell=cv2.dilate(self.mask('style bell').astype('uint8'),np.ones((5,5),np.uint8)).astype(bool)
        return np.where(bell,fine,general)

    def __init__(self,pass_directory=None):
        super().__init__(pass_directory or ROOT/'build/passes')
        self.wall=self.mask('room rear low wall','room rear header','room window pier','room side wall')
        self.floor=self.mask('room oak floorboard','room floor foundation','room woven rug')
        self.city=self.mask('sky')
        self.desk=self.mask('desktop','riser')
        # Warm wood and a darker, cool window form the same large colour masses
        # as the reference. Geometry and the user's photographs stay intact.
        def recolor(mask,color,strength=1):
            shade=np.clip(luma(self.A)/np.maximum(blur(luma(self.A),18),.05),.65,1.3)
            target=hexc(color)*shade[...,None]
            self.A=np.where(mask[...,None],mix(self.A,np.clip(target,0,1),strength),self.A)
        recolor(self.wall,'#dacba2',.7)
        recolor(self.desk,'#b9783d',.82)
        sky_shade=np.clip(luma(self.A),0,1)
        self.A=np.where(self.city[...,None],hexc('#25375f')*(.65+sky_shade[...,None]*.65),self.A)
        recolor(self.mask('window mullion','window rail'),'#202531',.95)
        recolor(self.mask('room oak floorboard','room floor foundation'),'#7c9ccb',.8)
        # Avoid the earlier overfilled lighting: most pixels previously clipped
        # above the compositor's light threshold, eliminating shadow levels.
        self.L['sky']*=.30
        self.L['sun']*=1.65
        for group in ['screen','rgb','lamp']:
            p=ROOT/'build/style-lights'/f'light_{group}.exr'
            if not p.exists():raise FileNotFoundError('Run style_lights.py first: '+str(p))
            self.L[group]=cv2.imread(str(p),cv2.IMREAD_UNCHANGED)[...,2::-1].astype(np.float32)
        self._edges()
        # Small bead seams should not become solid ink, while the silhouette
        # still participates in every style's line and shading system.
        pearl=self.mask('carousel')
        silhouette=(cv2.dilate(pearl.astype('uint8'),np.ones((3,3),np.uint8))-cv2.erode(pearl.astype('uint8'),np.ones((3,3),np.uint8)))>0
        self.e_outer=np.where(pearl&~silhouette,self.e_outer*.28,self.e_outer)
        self.e_detail=np.where(pearl,self.e_detail*.45,self.e_detail)
        bell=self.mask('style bell')
        bell_edge=(cv2.dilate(bell.astype('uint8'),np.ones((3,3),np.uint8))-cv2.erode(bell.astype('uint8'),np.ones((3,3),np.uint8)))>0
        self.e_outer=np.where(bell&~bell_edge,self.e_outer*.08,self.e_outer)
        self.e_inner=np.where(bell,self.e_inner*.15,self.e_inner)
        self.e_detail=np.where(bell,self.e_detail*.2,self.e_detail)

def main():
    stats={}
    for style in STYLES:
        c=DeskCtx()
        if style=='noir':
            # Clouds should read as a quiet night sky, not isolated white stains.
            c.A[c.city]=hexc('#182138')
        if style=='neon':
            c.E[c.mask('uplighter')]*=.35
            c.L['lamp']*=.35
        result=RENDER[style](c)
        # Orange accents in the monochrome ink edition belong to Mira's own
        # pineapple cup, rather than upstream object names that do not exist.
        if style=='void':
            accent=c.mask('pineapple pen cup')
            result=np.where(accent[...,None],result*hexc('#ff741f'),result)
        result=np.clip(result,0,1)
        image=Image.fromarray(np.rint(result*255).astype('uint8'))
        image.save(OUT/f'{style}.webp',quality=94)
        image.resize((480,270),Image.Resampling.LANCZOS).save(OUT/f'{style}-thumb.webp',quality=85)
        stats[style]={'wall_pixels':int(c.wall.sum()),'floor_pixels':int(c.floor.sum()),'window_pixels':int(c.city.sum()),'size':list(image.size),'bytes':(OUT/f'{style}.webp').stat().st_size}
        print('STYLE_READY',style,flush=True)
    (ROOT/'build/style-audit.json').write_text(json.dumps(stats,indent=2))
if __name__=='__main__':main()
