"""Build the approved shared extended timing and three full-length audio masters.

Requires every authorized voice clip first. Original Yue samples remain in order
at 1x; only quiet gaps are inserted. No generated clip is cropped or accelerated.
"""
from pathlib import Path
import json, math, re, subprocess, hashlib, sys
import numpy as np

V=Path(__file__).resolve().parents[1]; preview='--yue-preview' in sys.argv
Q=V/('qa/v13/full/yue-preview-r01' if preview else 'qa/v13/full/final-r01');Q.mkdir(parents=True,exist_ok=True)
D=V/('public/music/hk-v13-preview' if preview else 'public/music/hk-v13')
SR=48000; FPS=30; SPF=SR//FPS
def load(p): return json.loads(p.read_text())
def read(p):
 return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-ar',str(SR),'-ac','2','-f','f32le','-']),dtype='<f4').reshape(-1,2).copy()
def write(p,a):
 assert not p.exists(),f'Refuse overwrite: {p}'
 p.parent.mkdir(parents=True,exist_ok=True)
 subprocess.run(['ffmpeg','-v','error','-n','-f','f32le','-ar',str(SR),'-ac','2','-i','-','-c:a','pcm_s24le',str(p)],input=a.astype('<f4').tobytes(),check=True)
def measure(p):
 r=subprocess.run(['ffmpeg','-hide_banner','-i',str(p),'-af','loudnorm=I=-14.5:TP=-1.3:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
 return json.loads(re.findall(r'\{\s*"input_i".*?\}',r.stderr,re.S)[-1])
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

text=load(V/'qa/v13/full/final-r01/text-source.json'); captions=text['captions']; people=text['people']
city_sync=None if preview else load(V/'qa/v13/full/final-r01/city-voice-synchronization.json')
locales=['yue','en','zh-CN']; folder={'yue':'yue','en':'en','zh-CN':'cn'}
clips={}; missing=[]
for locale in locales:
 for cue in ([] if locale=='yue' else captions)+people:
  id=cue['id'] if cue['id'].startswith('caption-') else 'people-'+cue['id']
  selected='caption-07-r02' if locale=='en' and id=='caption-07' and not preview else id
  if locale=='zh-CN' and id=='caption-06' and not preview:selected='caption-06-r02'
  if id=='caption-12' and locale!='yue' and not preview:selected='caption-12-city-aligned'
  p=V/f'public/vo/hk-v13/{folder[locale]}/{selected}.wav'
  if not p.exists(): missing.append(str(p.relative_to(V)))
  else: clips[locale,id]=read(p)
if missing:
 (Q/'missing-voice-files.json').write_text(json.dumps(missing,ensure_ascii=False,indent=2)+'\n')
 if not preview:raise SystemExit(f'{len(missing)} normalized voice clips are still required; no final timeline/master emitted.')
 for p in people:assert ('yue','people-'+p['id']) in clips,'Preview requires all real Yue recordings.'

old=read(V/'qa/v12/stage3/voice-timeline.wav'); assert len(old)==2103*SPF
# Each hold is inside a settled view, before the following transition begins.
hold_frames=[113,171,229,320,413,510,599,690,748,837,970,1069,1126,1212,1271,1315,1390,1467,1545,1638,1720,1805,1905,1980]
holds=[]; audio_inserts=[]; cue_rows=[]; shift=0
def quiet_cut(start,end):
 lo=round(start*SR);hi=round(end*SR); a=np.max(np.abs(old[lo:hi]),axis=1)
 # Choose an actual 20ms quiet run, not a single zero crossing inside speech.
 block=960; candidates=[]
 for j in range(0,len(a)-block+1,120):
  peak=float(a[j:j+block].max())
  if peak<10**(-45/20):candidates.append((abs(lo+j+block//2-(lo+hi)/2),lo+j+block//2,peak))
 if not candidates:raise RuntimeError(f'No verified quiet gap in {start}–{end}; do not cut voice.')
 _,cut,peak=min(candidates)
 return cut,peak

for i,c in enumerate(captions):
 longest=max([len(clips[l,c['id']])/SR for l in ['en','zh-CN'] if (l,c['id']) in clips])
 extra=max(0,math.ceil((longest+.12-(c['end']-c['start']))*FPS))
 start=c['start']*FPS+shift
 row={'id':c['id'],'startFrame':start,'originalStart':c['start'],'originalEnd':c['end'],'text':c['text'],'duration':{l:(c['end']-c['start'] if l=='yue' else len(clips[l,c['id']])/SR if (l,c['id']) in clips else 0) for l in locales}}
 if city_sync and c['id']=='caption-12':row['duration']['yue']+=city_sync['locales']['yue']['addedSeconds']
 cue_rows.append(row)
 if extra:
  next_start=captions[i+1]['start'] if i+1<len(captions) else 68
  cut,peak=quiet_cut(c['end']-.02,next_start-.02)
  holds.append({'sourceFrame':hold_frames[i],'frames':extra,'cueId':c['id'],'startFrame':hold_frames[i]+shift})
  moved=city_sync['locales']['yue']['addedSamples'] if city_sync and c['id']=='caption-12' else 0
  if moved:audio_inserts.extend(city_sync['locales']['yue']['events'])
  assert extra*SPF>=moved
  audio_inserts.append({'sample':cut,'frames':extra,'samples':extra*SPF-moved,'kind':'shared_body_hold','cueId':c['id'],'quiet20msPeak':peak})
  shift+=extra

def span(id,min_frames=0):
 return max(min_frames,math.ceil((max(len(clips[l,'people-'+id])/SR for l in locales if (l,'people-'+id) in clips)+.7)*FPS))
opening=span('opening');lau=span('david-lau',72);patrick=span('patrick-li',72)
ops=span('operations-compliance',144);cities=span('hong-kong-new-york',144);wall=span('partner-wall',90)
plan={'openingFrames':opening,'personFrames':[lau,patrick,ops//2,ops-ops//2,cities//2,cities-cities//2],'returnFrames':15,'exitFrames':6,'wallFrames':wall}
people_frames=opening+lau+patrick+ops+cities+21+wall
body_before=sum(h['frames'] for h in holds if h['sourceFrame']<1652)
people_start=1652+body_before
people_cut,people_quiet=quiet_cut(54.60,54.72)
audio_inserts.append({'sample':people_cut,'frames':people_frames,'kind':'people_insert','quiet20msPeak':people_quiet})
for row in cue_rows:
 if row['originalStart']>=55:row['startFrame']+=people_frames
starts=[0,opening,opening+lau,opening+lau+patrick,opening+lau+patrick+ops,opening+lau+patrick+ops+cities+21]
for p,start in zip(people,starts):
 cue_rows.append({'id':'people-'+p['id'],'startFrame':people_start+start+9,'text':p['text'],'duration':{l:len(clips[l,'people-'+p['id']])/SR if (l,'people-'+p['id']) in clips else 0 for l in locales}})
total=2103+shift+people_frames
timeline={'fps':30,'durationInFrames':total,'durationSeconds':total/30,'originalFrames':2103,'bodyExtraFrames':shift,'peopleFrames':people_frames,'peopleStartFrame':people_start,'peopleSourceFrame':1652,'peoplePlan':plan,'holds':holds,'cues':sorted(cue_rows,key=lambda c:c['startFrame']),'audioInsertions':sorted(audio_inserts,key=lambda a:a['sample']),'approval':'qa/v13/people/shared-timing-extension-approval.json'}
if city_sync:
 city_start=next(r['startFrame']/FPS for r in cue_rows if r['id']=='caption-12');sg_start=next(r['startFrame']/FPS for r in cue_rows if r['id']=='caption-13');markers=city_sync['targetSecondsFromCaption12Start']
 timeline['mapTiming']={'hongKong':city_start+markers['hk'],'shenzhen':{'start':city_start+markers['sz'],'duration':.45},'routes':[{'name':'紐約','start':city_start+markers['ny'],'duration':1.05,'main':True,'amplitude':9},{'name':'新加坡','start':sg_start,'duration':.85,'main':False,'amplitude':5}]}
 timeline['mapSceneStartSeconds']=(864+sum(h['frames'] for h in holds if h['sourceFrame']<864))/FPS

# Original Yue voice: preserve every old PCM sample and insert only zero samples.
pieces=[];last=0;sample_mappings=[];dest=0
for event in timeline['audioInsertions']:
 cut=event['sample'];part=old[last:cut];pieces.append(part)
 sample_mappings.append({'sourceStart':last,'sourceEnd':cut,'destStart':dest});dest+=len(part)
 added=event['samples'] if 'samples' in event else event['frames']*SPF
 pieces.append(np.zeros((added,2),np.float32));dest+=added;last=cut
pieces.append(old[last:]);sample_mappings.append({'sourceStart':last,'sourceEnd':len(old),'destStart':dest})
yue_original=np.concatenate(pieces);assert len(yue_original)==total*SPF
for m in sample_mappings:assert np.array_equal(yue_original[m['destStart']:m['destStart']+m['sourceEnd']-m['sourceStart']],old[m['sourceStart']:m['sourceEnd']])

# Extend selected A with 0.8s equal-power joins. All music comes from A.
music=read(V/'public/music/v12-stage3/A-edit-70.1s.wav'); n=round(.8*SR)
loop=music[round(38.5*SR):round(53.5*SR)]; insert_at=people_cut
required=(shift+people_frames)*SPF
extension=loop.copy()
def join(a,b):
 t=np.linspace(0,np.pi/2,n,endpoint=False,dtype=np.float64)[:,None]
 return np.concatenate([a[:-n],a[-n:]*np.cos(t)+b[:n]*np.sin(t),b[n:]]).astype(np.float32)
while len(extension)<required+2*n:extension=join(extension,loop)
extension=extension[:required+2*n]
music_extended=join(join(music[:insert_at],extension),music[insert_at:]);assert len(music_extended)==total*SPF
music_path=D/'A-extended.wav';write(music_path,music_extended)

reports={}
for locale in (['yue'] if preview else locales):
 voice=yue_original.copy() if locale=='yue' else np.zeros((total*SPF,2),np.float32)
 # The original accepted Yue bus is quieter than the -16LUFS normalized clips.
 # Keep original gain intact and lower only added recordings to its speech bus.
 for c in timeline['cues']:
  if locale=='yue' and c['id'].startswith('caption-'):continue
  a=clips[locale,c['id']];start=round(c['startFrame']*SPF)
  assert start+len(a)<=len(voice)
  voice[start:start+len(a)]+=a*10**(-6.5/20)
 vp=D/f'{folder[locale]}-voice.wav';write(vp,voice)
 mix=D/f'{folder[locale]}-pre-master.wav';gain=.70*10**(-1.5/20)
 graph=f'[1:a]asplit=2[vo][sc];[0:a]volume={gain}[bg];[bg][sc]sidechaincompress=threshold=.028:ratio=3:attack=25:release=450:knee=2:makeup=1[duck];[duck][vo]amix=inputs=2:normalize=0:duration=longest[out]'
 subprocess.run(['ffmpeg','-n','-v','error','-i',str(music_path),'-i',str(vp),'-filter_complex',graph,'-map','[out]','-ar',str(SR),'-c:a','pcm_s24le',str(mix)],check=True)
 m=measure(mix);out=D/f'{folder[locale]}-master.wav'
 af=f"loudnorm=I=-14.5:TP=-1.3:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true"
 subprocess.run(['ffmpeg','-n','-v','error','-i',str(mix),'-af',af,'-ar',str(SR),'-c:a','pcm_s24le',str(out)],check=True)
 reports[locale]={'voice':str(vp.relative_to(V)),'master':str(out.relative_to(V)),'loudness':measure(out),'sha256':sha(out),'sampleFrames':len(read(out))}
 assert reports[locale]['sampleFrames']==total*SPF
 assert abs(float(reports[locale]['loudness']['input_i'])+14.5)<.6
 assert float(reports[locale]['loudness']['input_tp'])<=-1.1

timeline['status']='provisional_yue_preview_pending_remaining_language_recordings' if preview else 'three_language_measured_timeline'
timeline_path=V/('src/config/timeline-v13-preview.json' if preview else 'src/config/timeline-v13.json');assert not timeline_path.exists();timeline_path.write_text(json.dumps(timeline,ensure_ascii=False,indent=2)+'\n')
(Q/'audio-verification.json').write_text(json.dumps({'reports':reports,'yueOriginalSamplesPreservedBeforeNewVoice':True,'sampleMappings':sample_mappings,'musicSource':'A only','musicJoinSeconds':.8,'musicInsertOriginalSample':insert_at,'musicInsertLengthFrames':shift+people_frames,'originalMixIdentity':'Not claimed: user-approved common holds require new timing and continuous music mastering.'},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'seconds':total/30,'frames':total,'peopleSeconds':people_frames/30,'bodyExtensionSeconds':shift/30},ensure_ascii=False))
