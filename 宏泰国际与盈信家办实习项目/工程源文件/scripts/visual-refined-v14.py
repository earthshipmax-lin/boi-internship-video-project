from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw
V=Path(__file__).resolve().parents[1];Q=V/'qa/v14';report={}
for loc in ['yue','en','cn']:
 t=json.loads((V/f'src/config/timeline-v14-{loc}.json').read_text());rows=[]
 for f in [0,5,10,15,24,36,48,60,72]:
  frame=round(t['sceneStarts']['roots']+f);im=np.array(Image.open(Q/f'frames/{loc}-f{frame}.png').convert('RGB'));crop=im[150:710,1060:1760];blue=(crop[:,:,2]>100)&(crop[:,:,0]<70)&(crop[:,:,1]<190);rows.append({'frame':frame,'elapsedSeconds':f/30,'bluePixels':int(blue.sum())})
 assert all(a['bluePixels']<=b['bluePixels'] for a,b in zip(rows,rows[1:]));assert rows[0]['bluePixels']<30 and rows[-1]['bluePixels']>100000
 report[loc]={'growth':rows}
canvas=Image.new('RGB',(1440,600),'#142632');draw=ImageDraw.Draw(canvas);t=json.loads((V/'src/config/timeline-v14-yue.json').read_text())
for i,f in enumerate([0,6,12,18,24,36]):
 frame=round(t['sceneStarts']['platform']+f);im=Image.open(Q/f'frames/yue-f{frame}.png').resize((480,270));x=i%3*480;y=i//3*300;canvas.paste(im,(x,y+30));draw.text((x+10,y+8),f'EVERGREEN entry / +{f/30:.2f}s',fill='white')
canvas.save(Q/'evergreen-entry.jpg',quality=94)
canvas=Image.new('RGB',(1920,570),'#142632');draw=ImageDraw.Draw(canvas)
before=V/'qa/v13/redesign/frames/yue-f1634.png';after=Q/f"frames/yue-f{round(t['sceneStarts']['platform']+110)}.png"
for i,p in enumerate([before,after]):canvas.paste(Image.open(p).resize((960,540)),(i*960,30));draw.text((i*960+12,8),'BEFORE v13' if i==0 else 'AFTER v14',fill='white')
canvas.save(Q/'platform-before-after.jpg',quality=94)
old=Image.open(V/'qa/v13/redesign/frames/yue-f2987.png').convert('RGB');new=Image.open(Q/f"frames/yue-f{round(t['sceneStarts']['roots']+72)}.png").convert('RGB')
a=np.array(old)[150:710,1060:1760].astype(float);b=np.array(new)[150:710,1060:1760].astype(float);report['finalOfficialTreeCrop']={'absolutePixelDifferenceMax':float(np.abs(a-b).max()),'mean':float(np.abs(a-b).mean()),'source':'Official supplied vector paths preserved; comparison is native PNG, not encoded H264.'}
(Q/'animation-visual-check.json').write_text(json.dumps(report,indent=2)+'\n');print({k:v['growth'][-1]['bluePixels'] for k,v in report.items() if 'growth' in v});print(report['finalOfficialTreeCrop'])
