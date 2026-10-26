"""Small original texture set for Mira's fixed-scene prototype."""
from pathlib import Path
import random
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/textures'
OUT.mkdir(parents=True, exist_ok=True)
def font(n, bold=False):
    return ImageFont.truetype('C:/Windows/Fonts/'+('msyhbd.ttc' if bold else 'msyh.ttc'), n)
def label(d, xy, text, size, color='#31453f', bold=False):
    d.text(xy, text, font=font(size,bold), fill=color)
im=Image.new('RGB',(1600,900),'#203e4b'); d=ImageDraw.Draw(im)
d.rectangle((0,0,1600,65),fill='#142e3b')
for i,c in enumerate(['#dc8162','#eacb79','#92b3a2']):d.ellipse((30+i*32,23,44+i*32,37),fill=c)
label(d,(160,14),'MIRA / SELECTED EXPERIENCE',22,'#e9e4cc')
label(d,(85,112),'我是谁',100,'#fff1d1',True)
label(d,(90,257),'产品经理 / 海外创业者 / AI 内容创作者',31,'#adc5c7')
d.line((90,335,1510,335),fill='#6c8990',width=2)
for i,(num,title,subtitle,body,color) in enumerate([
    ('01','大厂产品','字节跳动 · 去哪儿','从策略产品到用户体验','#e8c981'),
    ('02','海外创业','WorkfxAI · 跨境电商','把想法带到真实市场','#d89b86'),
    ('03','自由探索','AI · 内容 · 摄影','不断试验，也认真生活','#aac6ba')]):
    x=85+i*485
    d.rounded_rectangle((x,380,x+455,725),14,fill=color)
    label(d,(x+30,404),num,30,'#31434a')
    label(d,(x+30,473),title,53,'#203e4b',True)
    label(d,(x+30,574),subtitle,26,'#34474a')
    label(d,(x+30,640),body,23,'#43575b')
label(d,(90,797),'2017 — NOW      一路实践，一路生长',27,'#d2dcd3')
label(d,(1210,797),'阅读履历  ↗',30,'#f7d995')
im.save(OUT/'monitor.png')
im=Image.new('RGB',(1200,750),'#eed8b2'); d=ImageDraw.Draw(im)
d.rectangle((0,0,1200,70),fill='#e5c79d')
label(d,(45,21),'mira / little corner',22,'#795240')
d.rounded_rectangle((65,118,1135,660),24,fill='#f7edce',outline='#be8366',width=3)
d.ellipse((935,154,1055,274),fill='#cd7757')
label(d,(118,173),'HELLO, WORLD.',27,'#95674a')
label(d,(112,275),"Hi, I’m Mira",92,'#254751',True)
label(d,(120,435),'做产品，也探索生活。',40,'#385963')
label(d,(120,566),'SYDNEY   /   点击，认识我  ↗',27,'#95674a')
im.save(OUT/'laptop.png')
for f in ['carousel','desk']:
    im=Image.open(ROOT/f'site/assets/{f}-reference.jpg').convert('RGB')
    ImageOps.fit(im,(400,500)).save(OUT/f'{f}.jpg')
# Low-detail painted sky for the window, no dimensional floating leaf shapes.
im=Image.new('RGB',(1600,1000)); d=ImageDraw.Draw(im)
for y in range(1000):
    t=y/1000; d.line((0,y,1600,y),fill=tuple(round(a+(b-a)*t) for a,b in zip((107,177,216),(224,236,217))))
cloud=Image.new('RGBA',im.size); cd=ImageDraw.Draw(cloud)
for x,y,w,h in [(320,240,440,110),(1020,150,330,75),(860,570,300,85)]:
    cd.ellipse((x-w/2,y-h/2,x+w/2,y+h/2),fill=(255,250,228,180))
im=Image.alpha_composite(im.convert('RGBA'),cloud.filter(ImageFilter.GaussianBlur(32)))
# A restrained, out-of-focus tree outside the right window; no city or extra props.
leaves=Image.new('RGBA',im.size); ld=ImageDraw.Draw(leaves); rng=random.Random(71)
ld.line([(1610,1080),(1460,790),(1350,620),(1270,510)],fill=(71,108,109,125),width=17)
for bx,by in [(1350,620),(1440,750),(1510,870)]:
    for sign in [-1,1]:
        ex=bx+sign*170;ey=by-125
        ld.line((bx,by,ex,ey),fill=(78,119,116,100),width=7)
        for j in range(20):
            x=ex+rng.randrange(-125,130);y=ey+rng.randrange(-95,90);w=rng.randrange(20,56);h=rng.randrange(12,30)
            ld.ellipse((x-w,y-h,x+w,y+h),fill=(86+rng.randrange(20),134+rng.randrange(15),124+rng.randrange(20),rng.randrange(50,110)))
im=Image.alpha_composite(im,leaves.filter(ImageFilter.GaussianBlur(9)))
im.convert('RGB').save(OUT/'sky.png')
im=Image.new('RGB',(600,100),'#fff7e7'); d=ImageDraw.Draw(im)
label(d,(25,14),'little moments / our days',33,'#806b67')
im.save(OUT/'caption.png')
im=Image.new('RGB',(450,120),'#26393d'); d=ImageDraw.Draw(im)
label(d,(20,14),'MIRA  /  35',60,'#d8d5c3',True)
im.save(OUT/'camera-badge.png')

# Handwritten cover art belongs to the editable scene, not a fabricated journal entry.
im=Image.new('RGB',(900,1100),'#e9e0c5');d=ImageDraw.Draw(im)
hand=lambda n:ImageFont.truetype('C:/Windows/Fonts/simkai.ttf',n)
d.text((93,110),'AI',font=hand(146),fill='#344c45')
d.text((85,286),'随手记',font=hand(126),fill='#344c45')
d.line([(100,443),(373,451),(727,437)],fill='#b58b54',width=5)
d.text((97,516),'边做，边想。',font=hand(46),fill='#727861')
for yy,t in [(675,'正在做的事'),(771,'还想试试看')]:
    d.rectangle((102,yy+6,131,yy+35),outline='#69735f',width=3)
    d.text((160,yy),t,font=hand(42),fill='#69735f')
d.text((575,960),'Mira',font=hand(48),fill='#8c8268')
im.save(OUT/'notebook-cover.png')
