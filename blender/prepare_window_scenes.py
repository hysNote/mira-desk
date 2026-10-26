"""Preserve the accepted website, and extract the real visible outdoor aperture."""
from pathlib import Path
import json,hashlib,shutil
import numpy as np
from PIL import Image
import cv2
ROOT=Path(__file__).resolve().parents[1];site=ROOT/'site';backup=site/'preserved-window'
if not backup.exists():
    backup.mkdir()
    for p in site.iterdir():
        if p.is_file():shutil.copy2(p,backup/p.name)
    for name in ['assets','layouts']:
        shutil.copytree(site/name,backup/name)
    records={str(p.relative_to(backup)):hashlib.sha256(p.read_bytes()).hexdigest() for p in backup.rglob('*') if p.is_file()}
    (ROOT/'build/before-window-scenes.json').write_text(json.dumps(records,indent=2))
meta=json.loads((ROOT/'build/passes/scene.json').read_text(encoding='utf-8'))
sky=next(o['color'] for o in meta['ids'] if o['object']=='sky')
ids=np.asarray(Image.open(ROOT/'build/passes/id.png').convert('RGB'))
# ID PNG has 8-bit dithering; decode the 16-step ID lattice, as the stylizer does.
mask=np.all(np.rint(ids.astype('float32')/16)==np.rint(np.array(sky)/16),axis=-1).astype('uint8')*255
assert mask.shape==(1080,1920)
# Keep existing frame/leaf ink at silhouette edges. Never paint over foreground.
alpha=cv2.GaussianBlur(cv2.erode(mask,np.ones((5,5),np.uint8)),(5,5),.75)
alpha=np.minimum(alpha,mask)
assert (alpha>250).sum()>.9*(mask>0).sum(),'Aperture unexpectedly fragmented'
out=site/'assets/windows';out.mkdir(exist_ok=True)
rgba=np.full((1080,1920,4),255,dtype=np.uint8);rgba[...,3]=alpha
Image.fromarray(rgba).save(out/'aperture.png')
ys,xs=np.where(mask>0)
report={'canvas':[1920,1080],'sky_color':sky,'bbox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'pixels':int((mask>0).sum()),'foreground_overwrite_pixels':int(((alpha>0)&(mask==0)).sum())}
(out/'aperture.json').write_text(json.dumps(report,indent=2));print(report)
