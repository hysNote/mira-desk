from pathlib import Path
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[1];p=root/'build/mira-block-cat/frame-audit'
frames=[p/f'{f:03d}.png' for f in range(1,242)]
assert all(f.exists() for f in frames)
def sheet(items,name,cols=8,cell=(192,174)):
    w,h=cell;out=Image.new('RGB',(cols*w,((len(items)+cols-1)//cols)*h),'#e5e5df');d=ImageDraw.Draw(out)
    for i,f in enumerate(items):
        x=i%cols*w;y=i//cols*h
        out.paste(Image.open(f).convert('RGB').resize((w,h-14),Image.Resampling.LANCZOS),(x,y+14));d.text((x+3,y+1),f.stem,fill='#222222')
    out.save(p/name)
for i in range(4):sheet(frames[i*64:(i+1)*64],f'sheet-{i+1}.jpg')
sheet(sorted(p.glob('rear-*.png')),'rear-sheet.jpg',4,(320,280))
sheet([p/f'{f:03d}.png' for f in [145,151,157,161,163,165,167,169,171,175,181,187]],'lower-paw-detail.jpg',4,(320,280))
imgs=[Image.open(f).convert('RGB').resize((360,300),Image.Resampling.LANCZOS) for f in frames[::2]]
imgs[0].save(p/'full-cycle.gif',save_all=True,append_images=imgs[1:],duration=67,loop=0)
print('241 frames, 4 sheets, rear sheet, paw detail and full-cycle GIF ready')
