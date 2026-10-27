"""Align the three city names by adding only measured quiet pauses, never stretching speech."""
from pathlib import Path
import json,subprocess
import numpy as np
V=Path(__file__).resolve().parents[1];SR=48000;Q=V/'qa/v13/full/final-r01'
def read(p):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-ar','48000','-ac','2','-f','f32le','-']),dtype='<f4').reshape(-1,2).copy()
def quiet(a,start,end):
 lo=round(start*SR);hi=round(end*SR);n=480;c=[]
 for i in range(lo,hi-n+1,60):
  peak=float(np.max(abs(a[i:i+n])))
  if peak<10**(-45/20):c.append((abs(i+n/2-(lo+hi)/2),i+n//2,peak))
 if not c:raise RuntimeError(f'No10ms quiet seam in {start}-{end}; no voice may be split.')
 _,cut,peak=min(c);return cut,peak
def pad(a,events):
 parts=[];last=0;mapping=[];pos=0
 for e in sorted(events,key=lambda e:e['sample']):
  k=e['sample'];parts.append(a[last:k]);mapping.append((last,k,pos));pos+=k-last
  parts.append(np.zeros((e['samples'],2),np.float32));pos+=e['samples'];last=k
 parts.append(a[last:]);mapping.append((last,len(a),pos));out=np.concatenate(parts)
 for lo,hi,dest in mapping:assert np.array_equal(out[dest:dest+hi-lo],a[lo:hi])
 return out,mapping
raw={'yue':{'hk':.18,'sz':.96,'ny':1.32,'hkEnd':.56,'szEnd':1.22},'en':{'hk':.72,'sz':1.82,'ny':2.78,'hkEnd':1.48,'szEnd':2.32},'zh-CN':{'hk':.56,'sz':1.32,'ny':1.96,'hkEnd':.98,'szEnd':1.78}}
target={'hk':max(r['hk'] for r in raw.values())}
target['sz']=max(r['sz']+target['hk']-r['hk'] for r in raw.values())
target['ny']=max(r['ny']+target['sz']-r['sz'] for r in raw.values())
report={'targetSecondsFromCaption12Start':target,'rawWordMarkers':raw,'sourceEvidence':['qa/v11/film/forced-alignment.json','qa/v13/full/final-r01/speech-audit/en-caption-12.json','qa/v13/full/final-r01/speech-audit/zh-CN-caption-12.json'],'locales':{},'limit':'Reference alignment supplies word windows; each edit seam separately requires a low-energy interval. Adds pauses only, no speech samples removed or altered.'}
for locale,r in raw.items():
 delays=[target['hk']-r['hk'],target['sz']-r['sz']-(target['hk']-r['hk']),target['ny']-r['ny']-(target['sz']-r['sz'])]
 assert min(delays)>-1e-6 and max(delays)<1
 src=V/('qa/v12/stage3/voice-timeline.wav' if locale=='yue' else f"public/vo/hk-v13/{'cn' if locale=='zh-CN' else 'en'}/caption-12.wav")
 a=read(src);offset=33.2 if locale=='yue' else 0;events=[]
 for i,delay in enumerate(delays):
  n=round(delay*SR)
  if not n:continue
  if i==0:
   cut,peak=quiet(a,32.7,33.15) if locale=='yue' else (0,0)
  else:cut,peak=quiet(a,offset+r['hkEnd' if i==1 else 'szEnd'],offset+r['sz' if i==1 else 'ny'])
  events.append({'sample':cut,'samples':n,'quiet10msPeak':peak,'kind':'city_word_alignment','beforeCity':['hk','sz','ny'][i]})
 out,mapping=pad(a,events);selected=None
 if locale!='yue':
  p=src.with_name('caption-12-city-aligned.wav');assert not p.exists()
  subprocess.run(['ffmpeg','-n','-v','error','-f','f32le','-ar','48000','-ac','2','-i','-','-c:a','pcm_s24le',str(p)],input=out.astype('<f4').tobytes(),check=True)
  decoded=read(p);assert np.max(abs(decoded-out))<2e-7;selected=str(p.relative_to(V))
 report['locales'][locale]={'events':events,'addedSamples':len(out)-len(a),'addedSeconds':(len(out)-len(a))/SR,'sourceSamplesPreserved':True,'selected':selected,'sampleMappings':mapping}
(Q/'city-voice-synchronization.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({l:r['addedSeconds'] for l,r in report['locales'].items()}))
