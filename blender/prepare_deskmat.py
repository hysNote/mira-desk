"""Derive a real die-cut mesh outline from the generated transparent texture."""
from pathlib import Path
import json
import cv2
root=Path(__file__).resolve().parents[1]
image=cv2.imread(str(root/'build/textures/tiger-deskmat.png'),cv2.IMREAD_UNCHANGED)
assert image is not None and image.shape[2]==4,'Desk mat needs an RGBA texture'
alpha=(image[:,:,3]>150).astype('uint8')*255
contours,_=cv2.findContours(alpha,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
contour=cv2.approxPolyDP(max(contours,key=cv2.contourArea),1.5,True).reshape(-1,2)
h,w=image.shape[:2]
points=[[float(x/w),float(1-y/h)] for x,y in contour]
area=sum(points[i][0]*points[(i+1)%len(points)][1]-points[(i+1)%len(points)][0]*points[i][1] for i in range(len(points)))
if area<0:points.reverse()
(root/'build/textures/tiger-deskmat-outline.json').write_text(json.dumps({'width':w,'height':h,'points':points}))
print('Desk mat silhouette:',len(points),'vertices')
