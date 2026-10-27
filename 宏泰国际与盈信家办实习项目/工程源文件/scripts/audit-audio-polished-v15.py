from pathlib import Path
import json,subprocess
import numpy as np
V=Path(__file__).resolve().parents[1];Q=V/'qa/v15';SR=48000;G=10**(1.5/20)
def read(p):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-f','f32le','-ar','48000','-ac','2','-']),dtype='<f4').reshape(-1,2)
r={}
for loc in ['yue','en','cn']:
 old=read(V/f'public/music/hk-v14/{loc}-voice.wav');new=read(V/f'public/music/hk-v15/{loc}-voice.wav');n=len(old)
 if loc=='cn':n=round(json.loads((Q/'cn-audio.json').read_text())['ending']['insertStartSeconds']*SR)
 e=float(np.abs(new[:n]-old[:n]*G).max());assert e<3e-7
 a=read(V/f'public/music/hk-v14/{loc}-music.wav');b=read(V/f'public/music/hk-v15/{loc}-music.wav');me=float(np.abs(b-a/G).max());assert me<3e-7
 r[loc]={'voiceSamplesCompared':n,'voiceExpectedGainDB':1.5,'voiceMaxAbsoluteSampleError':e,'musicExpectedGainDB':-1.5,'musicMaxAbsoluteSampleError':me,'timeStretch':False,'musicSource':'Existing A music only; B/C not read.'}
a=read(V/'public/vo/hk-v15/cn/ending-source-r01.wav');e=np.array([np.abs(a[i:i+480]).max() for i in range(0,len(a),480)]);runs=[];start=None
for i,v in enumerate(e):
 if v<10**(-40/20) and start is None:start=i
 if (v>=10**(-40/20) or i==len(e)-1) and start is not None:
  if i-start>=12:runs.append([start*.01,i*.01,(i-start)*.01])
  start=None
r['mandarinSource']={'quietRunsSeconds':runs,'durationSeconds':len(a)/SR,'thresholdDBFS':-40,'note':'Natural punctuation and explicit tags jointly produce pauses; labels do not equal measured silence.'}
(Q/'audio-boundary-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
