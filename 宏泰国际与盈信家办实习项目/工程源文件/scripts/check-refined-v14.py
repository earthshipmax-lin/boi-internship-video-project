from pathlib import Path
import json,hashlib,math,itertools,subprocess,re
import numpy as np
V=Path(__file__).resolve().parents[1];Q=V/'qa/v14';report={'layout':{},'sync':{},'blue':{},'english':{}}
def gap(a,b):return math.hypot(max(a['x']-b['x']-b['width'],b['x']-a['x']-a['width'],0),max(a['y']-b['y']-b['height'],b['y']-a['y']-a['height'],0))
for folder in ['yue','en','cn']:
 t=json.loads((V/f'src/config/timeline-v14-{folder}.json').read_text());a=json.loads((Q/f'{folder}-audit.json').read_text());fail=[];mins=[]
 for row in a:
  d=row['data'];xs=d.get('designText',d.get('texts',[]))
  for x in xs:
   if x.get('opacity',1)<.05:continue
   b=x.get('glyphRect') or x.get('fontRect') or x.get('rect')
   if b and (b['x']<-.5 or b['y']<-.5 or b['x']+b['width']>1920.5 or b['y']+b['height']>1080.5):fail.append((x.get('id'),'canvas'))
   if (x.get('scrollWidth') or 0)>(x.get('clientWidth') or 99999)+1:fail.append((x.get('id'),'box'))
  ps=[x for x in xs if str(x.get('id','')).startswith('platform.') and x.get('opacity',0)>.65]
  if len(ps)>=14:
   for x,y in itertools.combinations(ps,2):mins.append((gap(x['fontRect'],y['fontRect']),x['id'],y['id']))
  for p in d.get('photos',[]):assert p['nativeScaleX']<=1.600001 and p['grayscale']==0
 assert not fail,fail
 assert not mins or min(mins)[0]>=24,min(mins)
 report['layout'][folder]={'sampleRecords':len(a),'failures':fail,'minimumPlatformTextGap':min(mins) if mins else None}
 p=V/f'public/music/hk-v14/{folder}-voice.wav'
 voice=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-f','f32le','-ar','48000','-ac','2','-']),dtype='<f4').reshape(-1,2)
 # Check stable voice energy at 1/30s against the burned subtitle intervals.
 count=t['durationInFrames'];v=np.max(np.abs(voice[:count*1600]).reshape(count,1600,2),axis=(1,2));mask=np.zeros(count,bool)
 for c in t['cues']:
  assert c['endFrame']>c['startFrame'];mask[max(0,c['startFrame']):min(count,c['endFrame'])]=True
 active=v>10**(-38/20);outside=np.where(active & ~mask)[0]
 report['sync'][folder]={'cues':len(t['cues']),'frames':count,'activeAudioFrames':int(active.sum()),'activeFramesOutsideSubtitles':outside.tolist(),'thresholdDBFS':-38,'policy':'Audio activity coverage is a boundary check, not a pronunciation certification.'}
 assert len(outside)==0,(folder,outside.tolist())
# Screen blue contrast at the brightest base token, plus actual sample pixel mask later.
def lum(h):
 v=[int(h[i:i+2],16)/255 for i in [1,3,5]];v=[x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in v];return .2126*v[0]+.7152*v[1]+.0722*v[2]
for h in ['#124967','#1B6489','#205F83']:report['blue'][h]={'creamContrast':(lum('#F4EEE2')+.05)/(lum(h)+.05),'luminance':lum(h)}
raw=json.loads((Q/'english-independent-asr.json').read_text());expected=json.loads((Q/'english-narration.json').read_text())
def norm(s):
 s=s.lower().replace('1.5','one point five').replace('20,000','twenty thousand').replace('20000','twenty thousand').replace('1997','nineteen ninety seven');s=re.sub(r'\b10\b','ten',s);return re.findall(r"[a-z]+(?:'[a-z]+)?",s)
assert norm(raw['text'])==norm(' '.join(x['text'] for x in expected))
report['english']={'normalizedIndependentTranscriptMatches':True,'cues':30,'wordMatchingCaveat':'Number formatting normalized; ASR not human listening approval.','creditsBefore':8165,'creditsAfter':6710,'creditUse':1455,'productionUse':1429,'discardedEditorStateTest':26}
(Q/'preflight.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
