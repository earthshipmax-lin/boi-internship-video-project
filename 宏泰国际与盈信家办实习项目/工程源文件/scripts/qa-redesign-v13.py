from pathlib import Path
import json,math,itertools,subprocess
import numpy as np
from PIL import Image,ImageDraw
V=Path(__file__).resolve().parents[1];Q=V/'qa/v13/redesign';t=json.loads((V/'src/config/timeline-v13-redesign.json').read_text());old=t['sourceTimeline']
def oldframe(f):return f+sum(h['frames'] for h in old['holds'] if h['sourceFrame']<=f)+(t['peopleFrames'] if f>=1652 else 0)
def newframe(f):
 x=oldframe(f);return x-sum(min(c['frames'],max(0,x-c['startFrame'])) for c in t['redesignCuts'])
def rectgap(a,b):return math.hypot(max(a['x']-b['x']-b['width'],b['x']-a['x']-a['width'],0),max(a['y']-b['y']-b['height'],b['y']-a['y']-a['height'],0))
report={'platform':{},'map':{},'voice':{},'roots':{}}
for loc in ['yue','en','zh-CN']:
 p=Q/f'{loc}-layout-audit.json'
 if not p.exists():continue
 rows=json.loads(p.read_text());platform=next(r['data'] for r in rows if r['data'].get('sourceFrame')==1320)
 texts=[x for x in platform['designText'] if x['id'].startswith('platform.')]
 gaps=[(rectgap(a['fontRect'],b['fontRect']),a['id'],b['id']) for a,b in itertools.combinations(texts,2)]
 report['platform'][loc]={'minTextBoxGap':min(gaps),'minBodyFont':min(float(x['fontSize'].replace('px','')) for x in texts)}
 assert min(gaps)[0]>=24,min(gaps)
 root=next(r['data'] for r in rows if r['data'].get('sourceFrame')==1700)
 r=next(x for x in root['designText'] if x['id']=='roots.title')['fontRect'];c=r['y']+r['height']/2
 assert abs(c-430)<=20,(loc,c)
 report['roots'][loc]={'fontBoxCenterY':c,'treeCenterY':430,'centerDifference':abs(c-430)}
 # Ink measure is actual pixels, excludes brand, caption and underline.
 im=np.array(Image.open(Q/f'frames/{loc}-f{newframe(1700)}.png').convert('RGB'))
 ink=np.linalg.norm(im.astype(float)-[244,238,226],axis=2)>45
 left=int(ink[270:600,170:950].sum());right=int(ink[145:715,1055:1765].sum())
 report['roots'][loc].update({'textInkPixels':left,'treeInkPixels':right,'treeToTextInkRatio':right/left})
def project(lon,lat):return np.array([140+((lon+360 if lon<-40 else lon)+40)/360*1640,320+(80-lat)*4.4])
hk=project(114.1722,22.2988);sz=project(113.93,22.5333)
report['map']={'lensMagnification':44,'lensPointDistancePx':float(np.linalg.norm(hk-sz)*44),'coastVerification':'asset-projection-check.json','pathType':'single quadratic Q; no sampled path geometry'}
assert report['map']['lensPointDistancePx']>=60
# Exact quadratic extrema and all main-map city/name/planning-label boxes.
routes={}
for name,ll in [('NY',(-73.8303,40.758)),('SG',(103.851,1.283))]:
 q=project(*ll);v=q-hk;dist=float(np.linalg.norm(v));sign=-1 if v[0]>=0 else 1;b=(hk+q)/2+sign*np.array([-v[1],v[0]])/dist*max(60,dist*.28)
 points=[hk,q]
 for axis in [0,1]:
  den=hk[axis]-2*b[axis]+q[axis]
  if abs(den)>1e-9:
   u=(hk[axis]-b[axis])/den
   if 0<u<1:points.append((1-u)**2*hk+2*(1-u)*u*b+u*u*q)
 pts=np.array(points);mn=pts.min(axis=0);mx=pts.max(axis=0)
 routes[name]={'x':float(mn[0]),'y':float(mn[1]),'width':float(mx[0]-mn[0]),'height':float(mx[1]-mn[1])}
report['map']['routeBounds']=routes;report['map']['labelIntersectionFailures']=[]
for loc in ['yue','en','zh-CN']:
 p=Q/f'{loc}-layout-audit.json'
 if not p.exists():continue
 rows=json.loads(p.read_text());d=next(r['data'] for r in rows if r['data'].get('sourceFrame')==1138)
 labels=[x for x in d['designText'] if x['id'].startswith('map.')][:7]
 for label in labels:
  for name,b in routes.items():
   if rectgap(label['fontRect'],b)==0:report['map']['labelIntersectionFailures'].append([loc,name,label['id']])
assert not report['map']['labelIntersectionFailures'],report['map']['labelIntersectionFailures']
assets=json.loads((V/'src/config/awards-stage8.json').read_text())['items'];byid={x['id']:x for x in assets};boxes=[];x=520
for aid in ['native-a016','native-a008','native-a006','native-a010']:
 a=byid[aid];w=490*a['output_pixels'][0]/a['output_pixels'][1];boxes.append({'id':aid,'x':x,'y':370,'width':w,'height':490});x+=w+27
for i,aid in enumerate(['native-a004','native-a005']):
 a=byid[aid];w=600*a['output_pixels'][0]/a['output_pixels'][1];boxes.append({'id':aid,'x':130 if i==0 else 1790-w,'y':300,'width':w,'height':600})
assert all(rectgap(a,b)>0 for a,b in itertools.combinations(boxes,2))
report['awards']={'assetBoxes':boxes,'minimumGapPx':min(rectgap(a,b) for a,b in itertools.combinations(boxes,2)),'trophyBaselineDeviationPx':0,'removedFlatDocuments':['native-a012','native-a013','native-a014','native-a015']}
def read(p):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-f','f32le','-ac','2','-ar','48000','-']),dtype='<f4').reshape(-1,2)
for loc in ['yue','en','cn']:
 a=read(V/f'public/music/hk-v13/{loc}-voice.wav')
 for c in reversed(t['redesignCuts']):a=np.concatenate([a[:c['startFrame']*1600],a[c['endFrame']*1600:]])
 b=read(V/f'public/music/hk-v13-redesign/{loc}-voice.wav')
 delta=float(np.max(np.abs(a-b)));assert len(a)==len(b) and delta<=1/8388608
 report['voice'][loc]={'samplesPerChannel':len(b),'retainedSamplesMaxError':delta,'rate':1,'quietCutFrames':70}
(Q/'geometry-voice-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
# Same source-frame before/after comparisons; old frame is decoded H264, new is native PNG.
groups={'brands':[439,470,500,534],'awards':[712,735,795,860],'map':[875,950,1050,1138],'platform':[1150,1190,1280,1320],'roots':[1662,1700,1760,1805]}
D=Q/'comparison';D.mkdir(exist_ok=True)
for name,frames in groups.items():
 sheet=Image.new('RGB',(1920,4*570),'#151b21');draw=ImageDraw.Draw(sheet)
 for i,f in enumerate(frames):
  before=D/f'before-{f}.png'
  if not before.exists():subprocess.run(['ffmpeg','-v','error','-ss',str(oldframe(f)/30),'-i',str(V/'out/BOI-HK_史詩形象片_v13_粵語_加長版.mp4'),'-frames:v','1',str(before)],check=True)
  for j,p in enumerate([before,Q/f'frames/yue-f{newframe(f)}.png']):
   sheet.paste(Image.open(p).convert('RGB').resize((960,540)),(j*960,i*570+30))
  draw.text((15,i*570+8),f'{name} / source frame {f} / BEFORE (encoded)',fill='white');draw.text((975,i*570+8),'AFTER (native render)',fill='white')
 sheet.save(D/f'{name}-before-after.jpg',quality=94)
print(json.dumps(report,ensure_ascii=False))
