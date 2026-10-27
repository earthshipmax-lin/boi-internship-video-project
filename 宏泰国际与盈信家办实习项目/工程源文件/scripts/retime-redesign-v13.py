from pathlib import Path
import json,subprocess,re,math
import numpy as np
V=Path(__file__).resolve().parents[1];q=V/'qa/v13/redesign';D=V/'public/music/hk-v13-redesign';D.mkdir(parents=True,exist_ok=True);SR=48000;SPF=1600
old=json.loads((V/'src/config/timeline-v13.json').read_text());t=json.loads(json.dumps(old))
def read(p):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-f','f32le','-ar','48000','-ac','2','-']),dtype='<f4').reshape(-1,2).copy()
def write(p,a):
 assert not p.exists(),p
 subprocess.run(['ffmpeg','-v','error','-n','-f','f32le','-ar','48000','-ac','2','-i','-','-c:a','pcm_s24le',str(p)],input=a.astype('<f4').tobytes(),check=True)
def measure(p):
 r=subprocess.run(['ffmpeg','-hide_banner','-i',str(p),'-af','loudnorm=I=-14.5:TP=-1.3:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True);return json.loads(re.findall(r'\{\s*"input_i".*?\}',r.stderr,re.S)[-1])
voices={l:read(V/f'public/music/hk-v13/{l}-voice.wav') for l in ['yue','en','cn']};cuts=[]
blue_end=1323+sum(h['frames'] for h in old['holds'] if h['sourceFrame']<1323)
for a,b in zip(old['cues'],old['cues'][1:]):
 if not a['id'].startswith('caption-') or int(a['id'][-2:])>16:break
 end=max(a['startFrame']+a['duration'][l]*30 for l in ['yue','en','zh-CN']);gap=b['startFrame']-end;remove=min(15 if gap>60 else 8,max(0,math.floor(gap-6)))
 start=math.ceil(end+2);remove=min(remove,blue_end-start-1)
 if remove<1:continue
 peaks={l:float(np.max(np.abs(v[start*SPF:(start+remove)*SPF]))) for l,v in voices.items()}
 if max(peaks.values())>10**(-42/20):continue
 cuts.append({'startFrame':start,'endFrame':start+remove,'frames':remove,'after':a['id'],'peak':peaks})
def shifted(f):return f-sum(min(c['frames'],max(0,f-c['startFrame'])) for c in cuts)
for c in t['cues']:c['startFrame']=shifted(c['startFrame'])
t['durationInFrames']=old['durationInFrames']-sum(c['frames'] for c in cuts);t['durationSeconds']=t['durationInFrames']/30;t['peopleStartFrame']=shifted(old['peopleStartFrame']);t['redesignCuts']=cuts;t['sourceTimeline']=old;t['status']='prompt15_blue_gaps_shortened_shared_three_language';t['dataStartSeconds']=shifted(431+sum(h['frames'] for h in old['holds'] if h['sourceFrame']<431))/30
for key in ['hongKong']:t['mapTiming'][key]=shifted(old['mapTiming'][key]*30)/30
t['mapTiming']['shenzhen']['start']=shifted(old['mapTiming']['shenzhen']['start']*30)/30
for i,r in enumerate(t['mapTiming']['routes']):r['start']=shifted(old['mapTiming']['routes'][i]['start']*30)/30;r['duration']=.8;r['amplitude']=0
t['mapSceneStartSeconds']=shifted(old['mapSceneStartSeconds']*30)/30
music=read(V/'public/music/hk-v13/A-extended.wav')
def trim(a,music=False):
 b=a.copy();n=round(.06*SR)
 for c in reversed(cuts):
  s=c['startFrame']*SPF;e=c['endFrame']*SPF
  if music:
   ramp=np.linspace(0,1,n)[:,None];b=np.concatenate([b[:s-n],b[s-n:s]*(1-ramp)+b[e-n:e]*ramp,b[e:]])
  else:b=np.concatenate([b[:s],b[e:]])
 return b
write(D/'A-extended.wav',trim(music,True));reports={}
for l,v in voices.items():
 vp=D/f'{l}-voice.wav';write(vp,trim(v));mix=D/f'{l}-pre-master.wav';g=.70*10**(-1.5/20)
 graph=f'[1:a]asplit=2[vo][sc];[0:a]volume={g}[bg];[bg][sc]sidechaincompress=threshold=.028:ratio=3:attack=25:release=450:knee=2:makeup=1[duck];[duck][vo]amix=inputs=2:normalize=0:duration=longest[out]'
 subprocess.run(['ffmpeg','-v','error','-n','-i',str(D/'A-extended.wav'),'-i',str(vp),'-filter_complex',graph,'-map','[out]','-ar','48000','-c:a','pcm_s24le',str(mix)],check=True);m=measure(mix);out=D/f'{l}-master.wav';af=f"loudnorm=I=-14.5:TP=-1.3:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true";subprocess.run(['ffmpeg','-v','error','-n','-i',str(mix),'-af',af,'-ar','48000','-c:a','pcm_s24le',str(out)],check=True);reports[l]=measure(out)
(V/'src/config/timeline-v13-redesign.json').write_text(json.dumps(t,ensure_ascii=False,indent=2)+'\n');(q/'timing-mix-report.json').write_text(json.dumps({'cuts':cuts,'removedSeconds':sum(c['frames'] for c in cuts)/30,'durationSeconds':t['durationSeconds'],'voicePolicy':'Only measured common quiet gaps removed; no time-stretch or word/tail trim; all paper-section timing relative to its start preserved.','musicPolicy':'A only;60ms joins; same duck and mastering target','reports':reports},ensure_ascii=False,indent=2)+'\n');print('Shortened',sum(c['frames'] for c in cuts)/30,'seconds across',len(cuts),'gaps; new duration',t['durationSeconds'])
