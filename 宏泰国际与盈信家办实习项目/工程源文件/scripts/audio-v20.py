from pathlib import Path
import numpy as np,json,subprocess,hashlib
from scipy.signal import stft
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
V=Path(__file__).resolve().parents[1];Q=V/'qa/v20';D=V/'public/music/hk-v20';D.mkdir(exist_ok=True);SR=48000

def read(p):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-ar',str(SR),'-ac','2','-f','f32le','-']),dtype='<f4').reshape(-1,2).copy()
def write(p,a):
 if p.exists():return
 subprocess.run(['ffmpeg','-v','error','-n','-f','f32le','-ar',str(SR),'-ac','2','-i','-','-c:a','pcm_s24le',str(p)],input=a.astype('<f4').tobytes(),check=True)
reports={}
for loc in ['cn','en','yue']:
 t=json.load(open(V/f'src/config/timeline-v20-{loc}.json'));e=t['edit'];a=e['cutStart']*1600;b=e['cutEnd']*1600;r=e['rootsStart']*1600;gap=r-a
 master=read(V/f'public/music/hk-v{19 if loc=="cn" else 15}/{loc}-master.wav');voice=read(V/f'public/music/hk-v{19 if loc=="cn" else 15}/{loc}-voice.wav');music=read(V/f'public/music/hk-v15/{loc}-music.wav');pre=read(V/f'public/music/hk-v15/{loc}-pre-master.wav');ref=read(V/f'public/music/hk-v15/{loc}-master.wav');gain=float(np.sum(pre.astype('float64')*ref)/np.sum(pre.astype('float64')**2))
 # Keep original premix gain for voice; residual includes the previous duck curve.
 residual=master-voice*gain
 vo=np.concatenate([voice[:a],np.zeros((gap,2),dtype=np.float32),voice[b:]])
 write(D/f'{loc}-voice.wav',vo)
 reports[loc]={'prefixSamples':a,'suffixOriginalSample':b,'suffixNewSample':r,'voiceSuffixEqual':bool(np.array_equal(vo[r:],voice[b:])),'prefixEqual':True,'voiceGainForResidual':gain,'status':'two_music_join_auditions_pending_selection','candidates':[]}
 for variant,dur in [('A',gap/SR),('B',1.2)]:
  n=round(dur*SR);end=a+n
  # Equal-power music-only bridge; original voice is never stretched or faded.
  old=residual[a:a+n];newStart=b-gap
  nxt=residual[newStart:newStart+n];w=np.linspace(0,np.pi/2,n)[:,None];blend=old*np.cos(w)+nxt*np.sin(w)
  out=np.concatenate([master[:a],np.zeros((gap,2),dtype=np.float32),master[b:]])
  out[a:end]=blend+vo[a:end]*gain
  # Preserve master bit-exactly once bridge completes (including accepted CN ending).
  path=D/f'{loc}-candidate-{variant}.wav';write(path,out)
  start=max(0,a-10*SR);stop=start+20*SR;write(Q/f'{loc}-join-{variant}-20s.wav',out[start:stop])
  reports[loc]['candidates'].append({'id':variant,'crossfadeSeconds':dur,'prefixEqual':bool(np.array_equal(out[:a],master[:a])),'suffixAfterJoinEqual':bool(np.array_equal(out[end:],master[b+end-r:])),'audio':str(path.relative_to(V)),'previewStartSeconds':start/SR,'beatAligned':False})
  x=out[max(0,a-6*SR):min(len(out),a+6*SR)].mean(axis=1);fig,ax=plt.subplots(2,1,figsize=(12,5));ax[0].plot(np.arange(len(x))[::120]/SR-6,x[::120],lw=.4);ax[0].axvline(0,c='r');ax[0].set_title(f'{loc} candidate {variant}: provisional equal-power bridge; beat alignment NOT certified');ax[1].specgram(x,Fs=SR,NFFT=2048,noverlap=1536);ax[1].set_ylim(0,4000);fig.tight_layout();fig.savefig(Q/f'{loc}-join-{variant}-analysis.png');plt.close(fig)
(Q/'audio-candidates.json').write_text(json.dumps(reports,indent=2))
print('CANDIDATES READY')
