from pathlib import Path
import json,subprocess,numpy as np
from scipy.signal import stft,find_peaks,correlate
V=Path(__file__).resolve().parents[1];Q=V/'qa/v20'
def read(p):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-ar','12000','-ac','1','-f','f32le','-']),dtype='<f4')
reports={}
for loc in ['cn','en','yue']:
 p=V/f'public/music/hk-v15/{loc}-music.wav'
 if not p.exists():continue
 a=read(p);f,t,z=stft(a,12000,nperseg=1024,noverlap=904);spec=np.abs(z);flux=np.maximum(0,np.diff(spec,axis=1)).sum(axis=0);ac=correlate(flux-flux.mean(),flux-flux.mean(),mode='full')[len(flux)-1:];lags=np.arange(33,101);lag=lags[np.argmax(ac[lags])];bpm=6000/lag
 timeline=json.load(open(V/f'src/config/timeline-v20-{loc}.json'));e=timeline['edit'];delta=e['shiftFrames']/30
 peaks,_=find_peaks(flux,distance=int(lag*.7),prominence=np.std(flux)*.35)
 reports[loc]={'estimatedBPM':bpm,'autocorrelationLag':int(lag),'removedSeconds':delta,'phaseErrorSeconds':float(abs(delta-round(delta/(lag/100))*lag/100)),'onsetsNearCut':(t[1:][peaks][(t[1:][peaks]>e['cutStart']/30-4)&(t[1:][peaks]<e['cutStart']/30+4)]).tolist(),'onsetsNearSuffix':(t[1:][peaks][(t[1:][peaks]>e['cutEnd']/30-4)&(t[1:][peaks]<e['cutEnd']/30+4)]).tolist()}
(Q/'music-analysis.json').write_text(json.dumps(reports,indent=2));print(json.dumps(reports,indent=2))
