from pathlib import Path
from PIL import Image
import numpy as np
import cv2
import json
root=Path(__file__).resolve().parents[1]/'site/assets'
data=json.loads((root/'scene.json').read_text())
im=Image.open(root.parents[1]/'build/comic.png').convert('RGB')
# Preserve the upstream 16:9 camera frame in both appearance and hit map.
crop=(0,0,im.width,im.height)
im=im.crop(crop)
data['width'],data['height']=im.size
data['surfaces']={k:[[x,y-crop[1]] for x,y in pts] for k,pts in data['surfaces'].items()} if not data.get('cropped') else data['surfaces']
data['cropped']=True
im.save(root/'scene.webp',quality=92)
arr=np.asarray(Image.open(root/'hot.png').convert('RGB').crop(crop))
red=arr[:,:,0].astype(float)
index=np.clip(np.rint(red/28),0,len(data['keys'])).astype('uint8')
index[(np.abs(red-index*28)>3)|(arr[:,:,1]>3)|(arr[:,:,2]>3)]=0
Image.fromarray(index).save(root/'hot-index.png')
data['hots']={}
for i,key in enumerate(data['keys'],1):
    yy,xx=np.where(index==i)
    assert len(xx)>250,f'Missing visible hotspot {key}'
    bbox=[int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())]
    # A multi-part silhouette (e.g. three awards) can put its centroid on a
    # one-pixel edge. Use the largest interior disk so scaled clicks stay inside.
    distance=cv2.distanceTransform((index==i).astype('uint8'),cv2.DIST_L2,5)
    safe_y,safe_x=np.unravel_index(np.argmax(distance),distance.shape)
    data['hots'][key]={'index':i,'bbox':bbox,'center':[int(safe_x),int(safe_y)],'pixels':len(xx),'center_radius':round(float(distance[safe_y,safe_x]),2)}
    if key=='cat':
        im.crop((max(0,bbox[0]-25),max(0,bbox[1]-25),min(im.width,bbox[2]+25),min(im.height,bbox[3]+25))).save(root/'cat.webp',quality=90)
(root/'scene.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v['pixels'] for k,v in data['hots'].items()}))
