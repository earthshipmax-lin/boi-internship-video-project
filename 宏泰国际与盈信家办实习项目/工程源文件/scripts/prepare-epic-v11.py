from pathlib import Path
import json,subprocess,hashlib,re,math
import numpy as np
from PIL import Image,ImageDraw
from scipy.signal import find_peaks
ROOT=Path(__file__).resolve().parents[1];q=ROOT/'qa/v11/film';q.mkdir(parents=True,exist_ok=True)
def pcm(file,sr=11025):
 return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(file),'-ac','1','-ar',str(sr),'-f','f32le','-']),dtype='<f4')
a=pcm(ROOT/'public/music/v11/bgm-A.mp3');sr=11025;hop=128;nfft=1024
frames=np.lib.stride_tricks.sliding_window_view(a,nfft)[::hop]
spec=np.abs(np.fft.rfft(frames*np.hanning(nfft),axis=1));flux=np.maximum(0,np.diff(np.log1p(spec),axis=0)).mean(axis=1)
peaks,_=find_peaks(flux,height=np.percentile(flux,75),distance=int(.24*sr/hop),prominence=np.std(flux)*.15)
onsets=(peaks+1)*hop/sr
rms=[float(np.sqrt(np.mean(a[i:i+sr]**2))) for i in range(0,len(a),sr)]
meta={'source':'public/music/v11/bgm-A.mp3','source_sha256':hashlib.sha256((ROOT/'public/music/v11/bgm-A.mp3').read_bytes()).hexdigest(),'duration_s':len(a)/sr,'analysis':'Spectral positive flux, log-magnitude STFT 1024 / hop128 at11025Hz; peaks separated>=0.24s; not guaranteed musical downbeats','onsets_s':[round(float(v),5) for v in onsets],'rms_per_second':rms}
(q/'music-A-analysis.json').write_text(json.dumps(meta,indent=2)+'\n')
im=Image.new('RGB',(1500,360),'#0b2230');d=ImageDraw.Draw(im)
mx=max(rms)
for i,v in enumerate(rms):
 x=40+i*9;d.rectangle((x,300-v/mx*240,x+6,300),fill='#48adc7')
for i in range(0,155,10):d.text((40+i*9,315),str(i),fill='white')
im.save(q/'music-A-energy.png')
print('Music energy (5s bins):',[(i,round(float(np.mean(rms[i:i+5])),3)) for i in range(0,len(rms),5)],flush=True)
# Exact PDF crops, no alteration to content.
for source,name,box in [
 ('office-hk-source.png','hong-kong-office.jpg',(1430,368,3250,1120)),
 ('office-hk-source.png','hong-kong-building.jpg',(338,369,1380,1750)),
 ('awards-source.png','awards.jpg',(100,380,2110,1625))]:
 im=Image.open(q/source);im.crop(box).save(ROOT/'public/stills/v11'/name,quality=96)
# Reference-aware transcription is a timing aid, not a Cantonese language QA.
import torch,whisper
torch.set_num_threads(4)
model=whisper.load_model('tiny',device='cpu',download_root=str(ROOT/'.model-cache'))
res=model.transcribe(str(ROOT/'public/vo/hk-v11/full-r06.mp3'),language='zh',word_timestamps=True,fp16=False,condition_on_previous_text=False,initial_prompt=(ROOT/'qa/v11/voice-r06/script.txt').read_text(),verbose=False)
(q/'voice-timing-asr.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n')
for seg in res['segments']:print(round(seg['start'],2),round(seg['end'],2),seg['text'],flush=True)
