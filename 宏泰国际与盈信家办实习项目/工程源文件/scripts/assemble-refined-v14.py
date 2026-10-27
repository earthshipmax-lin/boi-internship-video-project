from pathlib import Path
import json,subprocess,re,math,hashlib
import numpy as np
V=Path(__file__).resolve().parents[1];Q=V/'qa/v14';D=V/'public/music/hk-v14';D.mkdir(parents=True,exist_ok=True);SR=48000;SPF=1600
old=json.loads((V/'src/config/timeline-v13-redesign.json').read_text());oldc=old['cues']
def read(p):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-ar','48000','-ac','2','-f','f32le','-']),dtype='<f4').reshape(-1,2).copy()
def write(p,a):
 assert not p.exists(),p
 subprocess.run(['ffmpeg','-v','error','-n','-f','f32le','-ar','48000','-ac','2','-i','-','-c:a','pcm_s24le',str(p)],input=a.astype('<f4').tobytes(),check=True)
def measure(p):
 r=subprocess.run(['ffmpeg','-hide_banner','-i',str(p),'-af','loudnorm=I=-14.5:TP=-1.3:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True);return json.loads(re.findall(r'\{\s*"input_i".*?\}',r.stderr,re.S)[-1])
def energy(a):
 n=480;mono=np.max(np.abs(a),axis=1);return np.array([mono[i:i+n].max() for i in range(0,len(mono),n)])
def speech_bounds(a,lo,hi):
 e=energy(a[int(lo*SR):int(hi*SR)]);active=np.where(e>10**(-43/20))[0];assert len(active),(lo,hi)
 # Include quiet natural tails; these are not re-synthesized or time-stretched.
 return max(lo,lo+active[0]*.01-.03),min(hi,lo+(active[-1]+1)*.01+.07)
def cut_audio(a,cuts,music=False):
 for c in reversed(cuts):
  s=c['start']*SPF;e=c['end']*SPF
  if music:
   n=min(2880,s);r=np.linspace(0,1,n)[:,None];a=np.concatenate([a[:s-n],a[s-n:s]*(1-r)+a[e-n:e]*r,a[e:]])
  else:a=np.concatenate([a[:s],a[e:]])
 return a
def source_frame(f):
 x=f+sum(h['frames'] for h in old['sourceTimeline']['holds'] if h['sourceFrame']<=f)+(old['peopleFrames'] if f>=1652 else 0)
 return x-sum(min(c['frames'],max(0,x-c['startFrame'])) for c in old['redesignCuts'])
all_reports={};music_old=read(V/'public/music/hk-v13-redesign/A-extended.wav')
for loc,folder in [('yue','yue'),('zh-CN','cn'),('en','en')]:
 path=V/f'src/config/timeline-v14-{folder}.json'
 if path.exists():continue
 cues=[];mapping=[];report={}
 if loc!='en':
  voice=read(V/f'public/music/hk-v13-redesign/{folder}-voice.wav');bounds=[]
  for i,c in enumerate(oldc):
   start=c['startFrame']/30;dur=c['duration'][loc]
   lo=max(0,start-.12);hi=min((oldc[i+1]['startFrame']/30-.08) if i+1<len(oldc) else old['durationSeconds'],start+dur+.12)
   s,e=speech_bounds(voice,lo,hi);bounds.append((s,e))
  cuts=[]
  for i,((s,e),(ns,ne)) in enumerate(zip(bounds,bounds[1:])):
   gap=ns-e;remove=min(.7,max(0,gap-.4));a=math.ceil((e+.09)*30);b=min(math.floor((ns-.1)*30),a+math.floor(remove*30))
   if b<=a:continue
   peak=float(np.abs(voice[a*SPF:b*SPF]).max())
   if peak>10**(-42/20):continue
   cuts.append({'start':a,'end':b,'frames':b-a,'after':oldc[i]['id'],'peak':peak})
  def shift(f):return f-sum(min(c['frames'],max(0,f-c['start'])) for c in cuts)
  total=old['durationInFrames']-sum(c['frames'] for c in cuts);last=0
  for c in cuts:
   if c['start']>last:mapping.append({'oldStart':last,'oldEnd':c['start'],'newStart':shift(last),'newEnd':shift(c['start'])})
   last=c['end']
  mapping.append({'oldStart':last,'oldEnd':old['durationInFrames'],'newStart':shift(last),'newEnd':total})
  for c,(s,e) in zip(oldc,bounds):cues.append({'id':c['id'],'startFrame':math.floor(shift(s*30)),'endFrame':math.ceil(shift(e*30))+2,'text':c['text'][loc],'speechStart':shift(s*30)/30,'speechEnd':shift(e*30)/30})
  voice= cut_audio(voice,cuts);music=cut_audio(music_old.copy(),cuts,True)
  report={'cuts':cuts,'removedSeconds':sum(c['frames'] for c in cuts)/30,'speechBoundsOld':bounds,'policy':'Only between-phrase measured quiet samples removed; no speaking-rate change.'}
 else:
  data=json.loads((Q/'english-alignment.json').read_text());raw=json.loads((Q/'english-independent-asr.json').read_text());source=read(V/'public/vo/hk-v14/en/full-source.wav');e=energy(source)
  quiet=[];a=None
  for i,v in enumerate(e):
   if v<10**(-42/20) and a is None:a=i
   if (v>=10**(-42/20) or i==len(e)-1) and a is not None:
    if i-a>=18:quiet.append((a*.01,i*.01))
    a=None
  words=[w for seg in raw['segments'] for w in seg.get('words',[])];rows=data['cues'];edges=[0.]
  for prev,c in zip(rows,rows[1:]):
   first_end=next((w['end'] for w in words if w['start']>=c['start']-.02 and w['end']>c['start']+.05),c['start']+.6)
   cand=[(a,b) for a,b in quiet if b>prev['end']-.1 and a<max(c['start']+.15,first_end)]
   assert cand,(prev['id'],c['id'],prev['end'],c['start'],first_end)
   target=(prev['end']+max(c['start'],prev['end']+.4))/2
   a,b=min(cand,key=lambda p:abs((p[0]+p[1])/2-target));edges.append((a+b)/2)
  edges.append(len(source)/SR)
  clips=[];new_starts=[];cursor=oldc[0]['startFrame'];mapping.append({'oldStart':0,'oldEnd':oldc[0]['startFrame'],'newStart':0,'newEnd':cursor})
  for i,row in enumerate(rows):
   assert row['id']==oldc[i]['id'],(row['id'],oldc[i]['id'])
   a,b=speech_bounds(source,edges[i],edges[i+1]);lo=max(edges[i],a-.04);hi=min(edges[i+1],b+.05);clip=source[round(lo*SR):round(hi*SR)]
   minframes=144 if row['id'] in ['people-operations-compliance','people-hong-kong-new-york'] else 84 if row['id'] in ['people-partner-wall'] else 0
   span=max(minframes,math.ceil((len(clip)/SR+.38)*30))
   if row['id']=='caption-10':span=max(span,96)
   if i==len(rows)-1:span=max(span,math.ceil((len(clip)/SR+1.1)*30))
   next_old=oldc[i+1]['startFrame'] if i+1<len(oldc) else old['durationInFrames'];mapping.append({'oldStart':oldc[i]['startFrame'],'oldEnd':next_old,'newStart':cursor,'newEnd':cursor+span})
   cues.append({'id':row['id'],'startFrame':cursor+math.floor((a-lo)*30),'endFrame':cursor+math.ceil((b-lo)*30)+2,'text':row['text'],'speechStart':cursor/30+a-lo,'speechEnd':cursor/30+b-lo})
   clips.append((cursor,clip));new_starts.append({'id':row['id'],'sourceSeconds':[lo,hi],'speechSeconds':[a,b],'spanFrames':span,'newStartFrame':cursor});cursor+=span
  total=int(cursor);voice=np.zeros((total*SPF,2),np.float32)
  for frame,clip in clips:voice[int(frame*SPF):int(frame*SPF)+len(clip)]+=clip
  peak=np.quantile(np.abs(voice),.999);voice*=min(2,.20/max(.001,peak))
  diff=len(music_old)-len(voice)
  if diff>=0:
   pos=round(70*SR);n=round(.15*SR);r=np.linspace(0,1,n)[:,None];music=np.concatenate([music_old[:pos-n],music_old[pos-n:pos]*(1-r)+music_old[pos+diff-n:pos+diff]*r,music_old[pos+diff:]])
  else:
   need=-diff;part=np.tile(music_old[round(60*SR):round(75*SR)],(math.ceil(need/(15*SR))+1,1))[:need];music=np.concatenate([music_old[:round(65*SR)],part,music_old[round(65*SR):]])
  report={'sourceClips':new_starts,'independentASRMatch':data['ratio'],'sourceSeconds':len(source)/SR,'cueCount':len(cues),'policy':'New approved-voice English narration, source chunks retained at1x; subtitles track measured voice onsets.'}
 assert len(voice)==total*SPF and len(music)==len(voice),(len(voice),total,len(music))
 def old_to_new(f):
  seg=next((s for s in mapping if s['oldStart']<=f<s['oldEnd']),None)
  if not seg:
   seg=next((s for s in mapping if s['oldStart']>=f),mapping[-1]);return seg['newStart']
  return seg['newStart']+(f-seg['oldStart'])*(seg['newEnd']-seg['newStart'])/(seg['oldEnd']-seg['oldStart'])
 for a,b in zip(cues,cues[1:]):a['endFrame']=min(a['endFrame'],b['startFrame']-1)
 starts={k:old_to_new(source_frame(f)) for k,f in [('data',431),('awards',705),('map',864),('platform',1141),('paper',1359),('people',1652),('roots',1652),('closing',1822)]}
 # Root scene starts AFTER people; source_frame(1652) includes insertion.
 starts['people']=old_to_new(old['peopleStartFrame'])
 byid={c['id']:c for c in cues};ct=byid['caption-12']
 if loc=='en':
  cr=next(c for c in report['sourceClips'] if c['id']=='caption-12');clip_start=cr['sourceSeconds'][0];dest=cr['newStartFrame']/30
  mk={}
  for name,phrase in [('hk','Hong'),('sz','Shenzhen'),('ny','New')]:
   hit=next(w for w in words if cr['sourceSeconds'][0]<=w['start']<=cr['sourceSeconds'][1] and w['word'].strip().lower().startswith(phrase.lower()))
   mk[name]=dest+hit['start']-clip_start
 else:mk={k:old_to_new(old['mapTiming'][{'hk':'hongKong','sz':'shenzhen','ny':'x'}[k]]*30)/30 if k=='hk' else old_to_new((old['mapTiming']['shenzhen']['start'] if k=='sz' else old['mapTiming']['routes'][0]['start'])*30)/30 for k in ['hk','sz','ny']}
 mt={'hongKong':mk['hk'],'shenzhen':{'start':mk['sz'],'duration':.45},'routes':[{'name':'紐約','start':mk['ny'],'duration':.8,'main':True,'amplitude':0},{'name':'新加坡','start':byid['caption-13']['speechStart'],'duration':.8,'main':False,'amplitude':0}]}
 timeline={'locale':loc,'fps':30,'durationInFrames':total,'durationSeconds':total/30,'map':mapping,'cues':cues,'oldTimeline':old,'sceneStarts':starts,'mapTiming':mt,'status':'measured_per_language_sync_refinement'}
 write(D/f'{folder}-voice.wav',voice)
 # Preserve a quiet ending and existing A source, with localized joins.
 music[-int(1.2*SR):]*=np.linspace(1,0,int(1.2*SR))[:,None]
 write(D/f'{folder}-music.wav',music)
 mix=D/f'{folder}-pre-master.wav';graph='[1:a]asplit=2[vo][sc];[0:a]volume=.589[bg];[bg][sc]sidechaincompress=threshold=.028:ratio=3:attack=25:release=450:knee=2:makeup=1[duck];[duck][vo]amix=inputs=2:normalize=0:duration=longest[out]'
 subprocess.run(['ffmpeg','-v','error','-n','-i',str(D/f'{folder}-music.wav'),'-i',str(D/f'{folder}-voice.wav'),'-filter_complex',graph,'-map','[out]','-ar','48000','-c:a','pcm_s24le',str(mix)],check=True)
 m=measure(mix);af=f"loudnorm=I=-14.5:TP=-1.3:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true";out=D/f'{folder}-master.wav'
 subprocess.run(['ffmpeg','-v','error','-n','-i',str(mix),'-af',af,'-ar','48000','-c:a','pcm_s24le',str(out)],check=True)
 path.write_text(json.dumps(timeline,ensure_ascii=False,indent=2)+'\n');report.update({'durationSeconds':total/30,'loudness':measure(out),'sceneStarts':starts,'cueTimingPolicy':'First audible sound through measured tail+2frames; next cue never overlaps.'})
 (Q/f'{folder}-timing-audio.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(loc,total/30,'seconds',flush=True)
