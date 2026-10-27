from pathlib import Path
import json,subprocess,re,math
import numpy as np
V=Path(__file__).resolve().parents[1];Q=V/'qa/v15';D=V/'public/music/hk-v15';D.mkdir(exist_ok=True);SR=48000;GAIN=10**(1.5/20)
def read(p):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-ar','48000','-ac','2','-f','f32le','-']),dtype='<f4').reshape(-1,2).copy()
def write(p,a):
 assert not p.exists(),p
 subprocess.run(['ffmpeg','-v','error','-n','-f','f32le','-ar','48000','-ac','2','-i','-','-c:a','pcm_s24le',str(p)],input=a.astype('<f4').tobytes(),check=True)
def measure(p):
 r=subprocess.run(['ffmpeg','-hide_banner','-i',str(p),'-af','loudnorm=I=-13.8:TP=-1.3:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True);return json.loads(re.findall(r'\{\s*"input_i".*?\}',r.stderr,re.S)[-1])
for loc in ['yue','en','cn']:
 if (D/f'{loc}-master.wav').exists():continue
 tpath=V/f'src/config/timeline-v15-{loc}.json';t=json.loads(tpath.read_text());voice=read(V/f'public/music/hk-v14/{loc}-voice.wav');music=read(V/f'public/music/hk-v14/{loc}-music.wav');report={'voiceGainDB':1.5,'musicGainDB':-1.5,'targetLUFS':-13.8,'targetTruePeakDBTP':-1.3}
 if loc=='cn':
  ending=read(V/'public/vo/hk-v15/cn/ending-source-r01.wav');cue=next(c for c in t['cues'] if c['id']=='caption-23');start=cue['startFrame']/30
  # Match active-speech RMS to the old ending, with 0.6 dB extra emphasis; no time stretching.
  def rms_active(a):
   e=np.max(np.abs(a),axis=1);return np.sqrt(np.mean(a[e>10**(-33/20)]**2))
  reference=voice[int(start*SR):];gain=float(rms_active(reference)/rms_active(ending)*10**(.6/20));ending*=gain
  voice[int(start*SR):]=0;at=round(start*SR);voice[at:at+len(ending)]=ending
  # Measure quiet portions within alignment windows, retaining quiet spoken tails in caption windows.
  env=np.max(np.abs(ending),axis=1);active=np.where(env>10**(-43/20))[0];first=active[active<round(4.05*SR)];company=active[active>=round(4.05*SR)]
  cue.update(startFrame=math.floor((start+first[0]/SR-.03)*30),endFrame=math.ceil((start+first[-1]/SR+.10)*30),speechStart=start+first[0]/SR,speechEnd=start+first[-1]/SR)
  last=next(c for c in t['cues'] if c['id']=='caption-24');last.update(startFrame=math.floor((start+company[0]/SR-.04)*30),endFrame=math.ceil((start+company[-1]/SR+.12)*30),speechStart=start+company[0]/SR,speechEnd=start+company[-1]/SR)
  report['ending']={'source':'public/vo/hk-v15/cn/ending-source-r01.wav','insertStartSeconds':start,'sourceSeconds':len(ending)/SR,'matchGainDB':20*math.log10(gain),'naturalSpeedPreserved':True,'caption23':cue,'caption24':last}
 voice*=GAIN;music/=GAIN
 write(D/f'{loc}-voice.wav',voice);write(D/f'{loc}-music.wav',music)
 graph='[1:a]asplit=2[vo][sc];[0:a]volume=.589[bg];[bg][sc]sidechaincompress=threshold=.028:ratio=3:attack=25:release=450:knee=2:makeup=1[duck];[duck][vo]amix=inputs=2:normalize=0:duration=longest[out]'
 mix=D/f'{loc}-pre-master.wav';subprocess.run(['ffmpeg','-v','error','-n','-i',str(D/f'{loc}-music.wav'),'-i',str(D/f'{loc}-voice.wav'),'-filter_complex',graph,'-map','[out]','-ar','48000','-c:a','pcm_s24le',str(mix)],check=True)
 m=measure(mix);af=f"loudnorm=I=-13.8:TP=-1.3:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true"
 out=D/f'{loc}-master.wav';subprocess.run(['ffmpeg','-v','error','-n','-i',str(mix),'-af',af,'-ar','48000','-c:a','pcm_s24le',str(out)],check=True)
 report['loudness']=measure(out);(Q/f'{loc}-audio.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');tpath.write_text(json.dumps(t,ensure_ascii=False,indent=2)+'\n');print(loc,'MIX READY',report['loudness']['input_i'],flush=True)
 def stamp(f):
  ms=round(f/30*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
 (Q/f'{loc}.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(c["startFrame"])} --> {stamp(c["endFrame"])}\n{c["text"]}' for i,c in enumerate(t['cues']))+'\n')
