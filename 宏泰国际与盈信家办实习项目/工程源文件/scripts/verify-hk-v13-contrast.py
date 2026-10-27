from pathlib import Path
import json,math
import numpy as np
from PIL import Image
V=Path(__file__).resolve().parents[1];Q=V/'qa/v13/full';checks=[]
def lum(a):
 v=a/255.;return np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)@np.array([.2126,.7152,.0722])
paper=np.array([244,238,226]);foreground=lum(paper)
for bp in (Q/'contrast-r02').glob('f*.png'):
 frame=bp.stem[1:];bg=np.array(Image.open(bp).convert('RGB')).astype(float)
 for locale in ['yue','en','zh-CN']:
  actual=np.array(Image.open(Q/f'base-r06/frames/{locale}-f{frame}.png').convert('RGB')).astype(float)
  for row in json.loads((Q/f'base-r06/{locale}-stills.json').read_text())[frame]['designText']:
   if row['opacity']<.99 or row['id']=='watermark':continue
   if row['color']!='rgb(244, 238, 226)' and row.get('fill')!='rgb(244, 238, 226)':continue
   b=row['fontRect'];x,y=max(0,math.floor(b['x'])),max(0,math.floor(b['y']));xx,yy=min(1920,math.ceil(b['x']+b['width'])),min(1080,math.ceil(b['y']+b['height']))
   a=actual[y:yy,x:xx];back=bg[y:yy,x:xx];mask=(np.max(abs(a-paper),axis=2)<=2)&(np.max(abs(back-paper),axis=2)>6)
   if not mask.any():continue
   if row.get('stroke')=='rgb(11, 49, 74)':back=np.full_like(back,[11,49,74])
   ratio=(foreground+.05)/(lum(back)+.05)
   checks.append({'locale':locale,'sourceFrame':int(frame),'id':row['id'],'minContrast':float(ratio[mask].min()),'pixels':int(mask.sum())})
fail=[x for x in checks if x['minContrast']<7]
out={'checks':checks,'failures':fail,'scope':'Core fully opaque cream glyph pixels at14 representative blue frames in3locales, underlying text-hidden native render; fades, source artwork, intentionally muted watermark excluded; SVG label outline counted as immediate backing. Not a measurement of every encoded video frame.'}
(Q/'contrast-r02/verification.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'checks':len(checks),'failures':fail,'minimum':min(c['minContrast'] for c in checks)},ensure_ascii=False))
