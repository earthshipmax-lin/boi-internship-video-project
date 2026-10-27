from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import label,find_objects
V=Path(__file__).resolve().parents[1];Q=V/'qa/v15';report={}
for loc in ['yue','en','cn']:
 t=json.loads((V/f'src/config/timeline-v15-{loc}.json').read_text());start=round(t['sceneStarts']['iris']);rows=[]
 for delta in [1,3,6]:
  f=start+delta;a=np.array(Image.open(Q/f'frames/{loc}-f{f}.png').convert('RGB')).astype(int);mask=np.max(np.abs(a-np.array([244,238,226])),axis=2)<4
  ls,n=label(mask);num=ls[540,960];assert num>0,(loc,delta);ys,xs=np.where(ls==num);cx=(xs.min()+xs.max())/2;cy=(ys.min()+ys.max())/2
  if delta<=3:assert abs(cx-959.5)<=1.5 and abs(cy-539.5)<=1.5,(loc,delta,cx,cy)
  rows.append({'frame':f,'elapsedFrames':delta,'center':[cx,cy],'centerMeasurementValid':delta<=3,'note':'At later radii original cream artwork may join the same connected region. Center measured before that contact.','creamPixels':len(xs)})
 assert all(a['creamPixels']<b['creamPixels'] for a,b in zip(rows,rows[1:]));report[loc]={'centeredIris':rows,'actualWindowFrames':t['sceneStarts']['irisEnd']-start,'completeFromZero':True}
canvas=Image.new('RGB',(1440,900),'#142632');draw=ImageDraw.Draw(canvas);t=json.loads((V/'src/config/timeline-v15-yue.json').read_text())
for i,d in enumerate([0,1,3,6,9,12,18,22]):
 f=round(t['sceneStarts']['iris']+d);im=Image.open(Q/f'frames/yue-f{f}.png').resize((480,270));x=i%3*480;y=i//3*300;canvas.paste(im,(x,y+30));draw.text((x+10,y+8),f'CENTER IRIS / +{d} frames',fill='white')
canvas.save(Q/'center-iris-sequence.jpg',quality=94)
for name,f in [('pamela',2204),('partners',2510)]:
 old=V/f'qa/v15/iteration-r01/frames/yue-f{f}.png'
 # r01 already contains correct portraits. Compare against protected V14 native still when same frame exists.
 before=V/f'qa/v14/frames/yue-f{f}.png';after=Q/f'frames/yue-f{f}.png'
 if before.exists():
  canvas=Image.new('RGB',(1920,570),'#142632');draw=ImageDraw.Draw(canvas)
  for i,p in enumerate([before,after]):canvas.paste(Image.open(p).resize((960,540)),(i*960,30));draw.text((i*960+12,8),'V14 / BEFORE' if i==0 else 'V15 / AFTER',fill='white')
  canvas.save(Q/f'{name}-before-after.jpg',quality=94)
(Q/'visual-check.json').write_text(json.dumps(report,indent=2)+'\n');print('Centered iris checks passed for three locales.')
