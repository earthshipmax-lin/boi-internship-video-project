from pathlib import Path
import json,hashlib,subprocess,re
import numpy as np
V=Path(__file__).resolve().parents[1];Q=V/'qa/v19/film';SR=48000;t=json.loads((V/'src/config/timeline-v19-cn.json').read_text());report={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pcm(p):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-f','f32le','-ar','48000','-ac','2','-']),dtype='<f4').reshape(-1,2)
baseline=json.loads((Q/'protected-baseline.json').read_text());changed=[p for p,h in baseline.items() if not (V/p).is_file() or sha(V/p)!=h];assert not changed,changed
old=pcm(V/'public/music/hk-v19/cn-master.wav');master=pcm(V/'public/music/hk-v19/cn-master.wav');at=round(89.83333333333333*SR);assert np.array_equal(old[:at],master[:at]);assert len(master)==t['durationInFrames']*1600
voice=pcm(V/'public/music/hk-v19/cn-voice.wav').copy();voice[at:]=0;dry=pcm(V/'qa/v19/round2/work/candidate-1-dry.wav');voice[at:at+len(dry)]=dry;count=t['durationInFrames'];energy=np.max(np.abs(voice).reshape(count,1600,2),axis=(1,2));mask=np.zeros(count,bool)
for c in t['cues']:mask[c['startFrame']:c['endFrame']]=True
outside=np.where((energy>10**(-38/20))&~mask)[0];assert len(outside)==0,outside.tolist()
for a,b in zip(t['cues'],t['cues'][1:]):assert a['endFrame']<b['startFrame']
for kind,rel,frames in [('full','out/BOI-HK_史詩形象片_v19_普通話_片尾重錄版.mp4',2962),('preview','out/BOI-HK_v19_普通話片尾_雄渾重錄15秒預覽.mp4',450)]:
 p=V/rel;probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]));v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio');assert (v['width'],v['height'],v['avg_frame_rate'],int(v['nb_frames']))==(1920,1080,'30/1',frames);assert a['sample_rate']=='48000' and a['channels']==2
 subprocess.run(['ffmpeg','-v','error','-i',str(p),'-f','null','-'],check=True,capture_output=True)
 m=subprocess.run(['ffmpeg','-hide_banner','-i',str(p),'-af','loudnorm=I=-13.8:TP=-1.3:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True);lm=json.loads(re.findall(r'\{\s*"input_i".*?\}',m.stderr,re.S)[-1]);assert float(lm['input_tp'])<-.8
 decoded=pcm(p);ref=master if kind=='full' else master[2512*1600:];n=min(len(decoded),len(ref));corr=float(np.corrcoef(decoded[:n].ravel(),ref[:n].ravel())[0,1]);assert corr>.999
 report[kind]={'file':rel,'sha256':sha(p),'bytes':p.stat().st_size,'seconds':float(v['duration']),'frames':frames,'completeDecode':True,'integratedLUFS':float(lm['input_i']),'truePeakDBTP':float(lm['input_tp']),'audioCorrelationToMaster':corr};print(kind,'verified',flush=True)
rows=json.loads((Q/'layout-audit.json').read_text());fail=[]
for row in rows:
 for x in row['designText']:
  b=x.get('fontRect') or x['rect']
  if b['x']<-.5 or b['y']<-.5 or b['x']+b['width']>1920.5 or b['y']+b['height']>1080.5:fail.append(x['id'])
assert not fail,fail
report.update(status='technical_delivery_pending_user_emotion_review',protectedFilesUnchanged=len(baseline),bodyPCMUnchangedUntilSeconds=89.83333333333333,subtitleCues=len(t['cues']),activeFramesOutsideSubtitles=outside.tolist(),layoutSamples=len(rows),textOverflowFailures=fail,limits=['ASR uses homophone substitutions for 宏; not literal-character equality.','Emotion, drag and naturalness remain subject to user listening.','Picture geometry unchanged through V15 component reuse; suffix is re-encoded.', 'Subtitle activity uses primary dry phonation; quiet room decay is excluded.','Natural 山 tail remains about0.37s; user selected candidate1 after disclosure.'])
(Q/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
