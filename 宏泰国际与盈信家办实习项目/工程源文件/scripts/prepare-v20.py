from pathlib import Path
import json,math,hashlib
V=Path(__file__).resolve().parents[1]; Q=V/'qa/v20';Q.mkdir(exist_ok=True)
def view(f,t):
 s=next((s for s in t['map'] if s['newStart']<=f<s['newEnd']),t['map'][-1]);o=s['oldStart']+(f-s['newStart'])*(s['oldEnd']-s['oldStart'])/(s['newEnd']-s['newStart'])
 for c in t['oldTimeline']['redesignCuts']:
  if o>=c['startFrame']:o+=c['frames']
  else:break
 z=t['oldTimeline']['sourceTimeline'];a=z['peopleStartFrame'];b=a+z['peopleFrames']
 if a<=o<b:raise ValueError(('people frame',f,o))
 if o>=b:o-=z['peopleFrames']
 shift=0
 for h in z['holds']:
  start=h['sourceFrame']+shift
  if o<start:break
  if o<start+h['frames']:return h['sourceFrame']
  shift+=h['frames']
 return min(z['originalFrames']-1,max(0,o-shift))
for loc in ['cn','yue','en']:
 t=json.loads((V/f'src/config/timeline-v{19 if loc=="cn" else 15}-{loc}.json').read_text());c20=next(c for c in t['cues'] if c['id']=='caption-20');c21=next(c for c in t['cues'] if c['id']=='caption-21')
 a=math.floor(t['sceneStarts']['people']);b=min(math.floor(t['sceneStarts']['roots']),c21['startFrame']-2)
 fade=math.ceil(c20['speechEnd']*30)+18;root=fade+10;delta=b-root
 cues=[]
 for c in t['cues']:
  if c['id'].startswith('people-'):continue
  c=c.copy()
  if c['startFrame']>=b:
   for k in ['startFrame','endFrame']:c[k]-=delta
   for k in ['speechStart','speechEnd']:c[k]-=delta/30
  cues.append(c)
 frames=[]
 for f in range(t['durationInFrames']-delta):
  old=f if f<a else a-1 if f<root else f+delta
  frames.append({'old':old,'source':view(max(old,math.ceil(t['sceneStarts']['roots'])) if f>=root else old,t)})
 starts={k:(v-delta if v>=b else v) for k,v in t['sceneStarts'].items() if k!='people'};starts['roots']=root
 out={'locale':t['locale'],'fps':30,'durationInFrames':len(frames),'durationSeconds':len(frames)/30,'cues':cues,'sceneStarts':starts,'originalSceneStarts':t['sceneStarts'],'mapTiming':t['mapTiming'],'frames':frames,'edit':{'cutStart':a,'cutEnd':b,'fadeStart':fade,'rootsStart':root,'shiftFrames':delta,'holdSeconds':.6,'exitFrames':9,'blankFrames':1},'status':'v20_in_progress'}
 (V/f'src/config/timeline-v20-{loc}.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(loc,len(frames)/30,out['edit'])
# Copy unaffected picture implementation, remove all people imports and unused wrapper.
s=(V/'src/scenes/ScenesPolishedV15.tsx').read_text();s=s[:s.index('export type FilmWithPeoplePropsV13=')];s='\n'.join(l for l in s.splitlines() if "from '../components/PeopleAccordionV15'" not in l)
s=s.replace('PlatformRefinedV14,RootsRefinedV14','PlatformRefinedV14').replace("import {fontsReadyV13}","import {RootsV20 as RootsRefinedV14} from '../components/RootsV20';\nimport {fontsReadyV13}").replace('FilmPicturePolishedV15','FilmPictureV20');(V/'src/scenes/ScenesV20.tsx').write_text(s)
# Protect previous project source and deliverables.
protected={str(p.relative_to(V.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for base in [V/'src',V.parent/'BOI-20261027-三语/04_最终交付'] for p in base.rglob('*') if p.is_file() and 'v20' not in str(p).lower()}
(Q/'protected.json').write_text(json.dumps(protected,ensure_ascii=False,indent=2))
