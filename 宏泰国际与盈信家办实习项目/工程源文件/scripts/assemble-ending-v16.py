from pathlib import Path
import json,subprocess,math,re
import numpy as np
V=Path(__file__).resolve().parents[1];Q=V/'qa/v16';D=V/'public/music/hk-v16';SR=48000

def read(p):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-f','f32le','-ar',str(SR),'-ac','2','-']),dtype='<f4').reshape(-1,2).copy()
def write(p,a):
 assert not p.exists(),p
 subprocess.run(['ffmpeg','-v','error','-n','-f','f32le','-ar',str(SR),'-ac','2','-i','-','-c:a','pcm_s24le',str(p)],input=a.astype('<f4').tobytes(),check=True)
def active_rms(a):
 e=np.max(np.abs(a),axis=1);return float(np.sqrt(np.mean(a[e>10**(-33/20)]**2)))
# Local vowel lengthening with FFmpeg WSOLA; consonant attacks and pitch are retained.
source=read(V/'public/vo/hk-v16/cn/ending-emotion-r02.wav');a=source.copy();edits=[]
windows=[('山',3.24,3.42,1.80),('泰',4.79,5.01,1.80),('际',6.10,6.38,1.60)]
for word,s,e,factor in reversed(windows):
 lo=round(s*SR);hi=round(e*SR);segment=source[lo:hi];assert np.mean(np.max(np.abs(segment),axis=1)>.008)>.35,(word,'unvoiced')
 out=subprocess.check_output(['ffmpeg','-v','error','-f','f32le','-ar',str(SR),'-ac','2','-i','-','-af',f'atempo={1/factor}','-f','f32le','-'],input=segment.astype('<f4').tobytes());out=np.frombuffer(out,dtype='<f4').reshape(-1,2).copy()
 # Match the joins over 8ms without shifting samples outside the selected vowel.
 n=min(384,len(segment)//4,len(out)//4);w=np.linspace(0,1,n)[:,None];out[:n]=segment[:n]*(1-w)+out[:n]*w;out[-n:]=out[-n:]*(1-w)+segment[-n:]*w
 a=np.concatenate([a[:lo],out,a[hi:]]);edits.append({'word':word,'sourceWindowSeconds':[s,e],'requestedFactor':factor,'addedSamples':len(out)-len(segment),'addedSeconds':(len(out)-len(segment))/SR})
edits.reverse()
def warp(x):
 return x+sum(r['addedSeconds']*max(0,min(1,(x-r['sourceWindowSeconds'][0])/(r['sourceWindowSeconds'][1]-r['sourceWindowSeconds'][0]))) for r in edits)
write(V/'public/vo/hk-v16/cn/ending-sustained-r02.wav',a)
# Retain all pre-ending V15 PCM exactly. A restrained crescendo supports the native emotional performance.
oldvoice=read(V/'public/music/hk-v15/cn-voice.wav');oldmaster=read(V/'public/music/hk-v15/cn-master.wav');music=read(V/'public/music/hk-v15/cn-music.wav');pre=read(V/'public/music/hk-v15/cn-pre-master.wav');start=89.83333333333333;at=round(start*SR)
base=active_rms(oldvoice[at:])/active_rms(a);times=np.arange(len(a))/SR;db=np.interp(times,[0,warp(1.64),warp(2.5),warp(3.42),warp(4.36),warp(6.4),len(a)/SR],[-.4,-.1,.65,.85,1.6,2.,1.6]);a*=base*10**(db[:,None]/20)
voice=oldvoice.copy();voice[at:]=0;voice[at:at+len(a)]=a;write(D/'cn-voice.wav',voice)
# Rebuild only the final mix with the existing A cue and its original fade.
endvoice=np.zeros_like(oldmaster[at:]);endvoice[:len(a)]=a;write(D/'ending-voice.wav',endvoice);write(D/'ending-music.wav',music[at:])
graph='[1:a]asplit=2[vo][sc];[0:a]volume=.589[bg];[bg][sc]sidechaincompress=threshold=.028:ratio=3:attack=25:release=450:knee=2:makeup=1[duck];[duck][vo]amix=inputs=2:normalize=0:duration=longest[out]'
premix=D/'ending-pre-master.wav';subprocess.run(['ffmpeg','-v','error','-n','-i',str(D/'ending-music.wav'),'-i',str(D/'ending-voice.wav'),'-filter_complex',graph,'-map','[out]','-ar',str(SR),'-c:a','pcm_s24le',str(premix)],check=True)
mask=np.max(np.abs(pre[at:]),axis=1)>.02;ratios=oldmaster[at:][mask]/np.where(np.abs(pre[at:][mask])>1e-5,pre[at:][mask],np.nan);master_gain=float(np.nanmedian(ratios));ending=read(premix)*master_gain
write(D/'ending-scaled.wav',ending);subprocess.run(['ffmpeg','-v','error','-n','-i',str(D/'ending-scaled.wav'),'-af','alimiter=limit=0.851:attack=5:release=60:level=false:latency=true','-ar',str(SR),'-c:a','pcm_s24le',str(D/'ending-limited.wav')],check=True)
ending=read(D/'ending-limited.wav');master=oldmaster.copy();n=min(len(ending),len(master)-at);master[at:at+n]=ending[:n];fade=1920;w=np.linspace(0,1,fade)[:,None];master[at:at+fade]=oldmaster[at:at+fade]*(1-w)+master[at:at+fade]*w
assert np.array_equal(master[:at],oldmaster[:at]);write(D/'cn-master.wav',master)
t=json.loads((V/'src/config/timeline-v15-cn.json').read_text());env=np.max(np.abs(a),axis=1);active=np.where(env>10**(-43/20))[0];split=round(warp(4.05)*SR);first=active[active<split];last=active[active>=split]
for cue,ix in [(next(c for c in t['cues'] if c['id']=='caption-23'),first),(next(c for c in t['cues'] if c['id']=='caption-24'),last)]:
 cue.update(startFrame=math.floor((start+ix[0]/SR-.04)*30),endFrame=math.ceil((start+ix[-1]/SR+.12)*30),speechStart=start+ix[0]/SR,speechEnd=start+ix[-1]/SR)
t['status']='v16_mandarin_emotional_crescendo_ending';(V/'src/config/timeline-v16-cn.json').write_text(json.dumps(t,ensure_ascii=False,indent=2)+'\n')
r={'source':'public/vo/hk-v16/cn/ending-emotion-r02.wav','selected':'public/vo/hk-v16/cn/ending-sustained-r02.wav','insertStartSeconds':start,'sourceSeconds':len(source)/SR,'sustainedSeconds':len(a)/SR,'vowelEdits':edits,'crescendoDB':[-.4,.85,2.0],'sourceMatchGainDB':20*math.log10(base),'masterScale':master_gain,'bodyUnchangedSamplesPerChannel':at,'bodyPCMExactlyEqual':True,'localPitchShift':False,'mixPolicy':'Original V15 master before 89.833333 seconds is retained exactly. Final A music/duck retained; no full-track normalization.','caption23':t['cues'][-2],'caption24':t['cues'][-1]};(Q/'audio-implementation.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps(r,ensure_ascii=False))
