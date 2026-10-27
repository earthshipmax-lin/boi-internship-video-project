from pathlib import Path
import subprocess,json,re
import numpy as np
V=Path(__file__).resolve().parents[1];Q=V/'qa/v13/redesign';report={}
def pcm(p):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-f','f32le','-ar','48000','-ac','2','-']),dtype='<f4').reshape(-1,2)
for loc,label in [('yue','粵語'),('en','英文'),('cn','簡中')]:
 movie=V/f'out/BOI-HK_史詩形象片_v13_{label}_重設計版.mp4';master=V/f'public/music/hk-v13-redesign/{loc}-master.wav'
 a=pcm(movie);b=pcm(master);n=min(len(a),len(b));corr=float(np.corrcoef(a[:n].ravel(),b[:n].ravel())[0,1]);assert corr>.999
 run=subprocess.run(['ffmpeg','-hide_banner','-i',str(movie),'-af','loudnorm=I=-14.5:TP=-1.3:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
 m=json.loads(re.findall(r'\{\s*"input_i".*?\}',run.stderr,re.S)[-1]);report[loc]={'masterCorrelation':corr,'decodedSamplesPerChannel':len(a),'masterSamplesPerChannel':len(b),'integratedLUFS':float(m['input_i']),'truePeakDBTP':float(m['input_tp']),'loudnessRange':float(m['input_lra'])}
 assert float(m['input_tp'])<0
(Q/'encoded-audio-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
