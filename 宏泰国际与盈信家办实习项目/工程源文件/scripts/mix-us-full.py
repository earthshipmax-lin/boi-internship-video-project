from pathlib import Path
import numpy as np,json,wave,subprocess,hashlib
R=Path(__file__).resolve().parents[1];q=R/'qa/us-v1-60s';out=R/'public/music/us-v1';T=json.loads((q/'timeline.json').read_text());sr=48000;N=60*sr
# Original sparse keyboard-like score, additive synthesis, no external recordings/samples.
source=np.zeros((156*sr,2),np.float32);notes=[]
for i,start in enumerate(np.arange(.6,154,3.7)):
 midi=[48,55,62,52,59,57,64,55,50,60,57][i%11];duration=5.2;t=np.arange(int(duration*sr))/sr;freq=440*2**((midi-69)/12);sig=np.zeros_like(t)
 for k,amp in [(1,1),(2,.32),(3,.12),(4,.055),(6,.02)]:sig+=amp*np.sin(2*np.pi*freq*k*t)*np.exp(-t*(.65+.14*k))
 sig*=np.minimum(1,t/.012)*(1-np.exp(-(duration-t)/.12));sig*=.3
 a=int(start*sr);n=min(len(sig),len(source)-a);pan=[-.22,.18,-.08,.25][i%4];source[a:a+n,0]+=sig[:n]*(1-pan);source[a:a+n,1]+=sig[:n]*(1+pan);notes.append({'time':float(start),'midi':midi,'duration':duration})
source*=.5/np.max(np.abs(source))
def save(path,a):
 with wave.open(str(path),'wb') as w:w.setnchannels(a.shape[1]);w.setsampwidth(2);w.setframerate(sr);w.writeframes((np.clip(a,-1,1)*32767).astype('<i2').tobytes())
save(out/'original-keyboard-source.wav',source)
B=json.loads((R/'src/config/beats-v11.json').read_text());edit=np.zeros((int(68.04*sr),2),np.float32)
for span in B['spans']:
 a=int(span['source_start']*sr);b=int(span['source_end']*sr);at=int(span['timeline_start']*sr);part=source[a:b].copy();n=min(len(part),len(edit)-at);part=part[:n];ramp=min(int(.4*sr),n)
 if at:part[:ramp]*=np.linspace(0,1,ramp)[:,None]
 part[-ramp:]*=np.linspace(1,0,ramp)[:,None];edit[at:at+n]+=part
music=edit[:N];voice=np.zeros((N,2),np.float32);gain=np.full(N,10**(-10/20),np.float32);time=np.arange(N)/sr
for s in T['scenes']:
 raw=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(R/'public'/s['source']),'-ar',str(sr),'-ac','1','-f','f32le','-']),dtype=np.float32);a=s['voiceStartFrame']*1600;b=a+len(raw);assert b<=N
 voice[a:b]+=raw[:,None]
 start=a/sr;end=b/sr;duck=10**(-18/20);gain[a:b]=duck
 # Fast attack before voice, recovery to bed level in .5s.
 pre=max(0,a-int(.12*sr));gain[pre:a]=np.minimum(gain[pre:a],np.linspace(10**(-10/20),duck,a-pre))
 post=min(N,b+int(.5*sr));gain[b:post]=np.minimum(gain[b:post],np.linspace(duck,10**(-10/20),post-b))
S0=T['scenes'][0];S5=T['scenes'][5];gain[:S0['endFrame']*1600]=0;gain[S5['startFrame']*1600:S5['endFrame']*1600]=0;gain[-int(1*sr):]*=np.linspace(1,0,int(1*sr));
# Short ramps outside silent sections prevent boundary clicks.
a=S0['endFrame']*1600;gain[a:a+int(.4*sr)]*=np.linspace(0,1,int(.4*sr))
a=S5['startFrame']*1600;b=S5['endFrame']*1600;gain[a-int(.15*sr):a]*=np.linspace(1,0,int(.15*sr));gain[b:b+int(.5*sr)]*=np.linspace(0,1,int(.5*sr))
music*=gain[:,None]
# Single global gain preserves voice and music relationship, no speech rate/pitch edits.
mix=(voice+music)*.75;voice*=.75;music*=.75
save(out/'full-review-mix.wav',mix);save(q/'voice-bus.wav',voice);save(q/'music-bus.wav',music)
peak=lambda a:float(20*np.log10(max(np.max(np.abs(a)),1e-12)))
checks=[]
for s in T['scenes']:
 a=s['voiceStartFrame']*1600;b=min(N,a+round(s['duration']*sr));vp=peak(voice[a:b]);mp=peak(music[a:b]);checks.append({'scene':s['id'],'voicePeakDBFS':vp,'musicPeakDBFS':mp,'separationDB':vp-mp});assert vp-mp>=12
assert peak(mix)<=-1;assert np.max(np.abs(music[:S0['endFrame']*1600]))==0;assert np.max(np.abs(music[S5['startFrame']*1600:S5['endFrame']*1600]))==0
roles={'music':{'status':'original_project_score','source':'original-keyboard-source.wav','creation':'Original deterministic sparse additive keyboard composition; no external samples, song, purchased or stock music. Created specifically for user project.','commercialUse':'No third-party composition or sample license dependencies introduced; deliverable may be used for this project subject to other release approvals.','instrument':'Synthesized soft keyboard, not a recorded acoustic piano','score':notes,'editSpans':B['spans'],'crossfade_s':.4,'adaptation':'Reuses existing68.03573s span/crossfade structure; trims assembled bed at60s and fades last1s. Source onset data are not reused as musical beat claims.','duckVoiceGainDB':-18,'bedGainDB':-10,'recoverySeconds':.5,'S0':'silent','S5':'silent'},'mix':{'globalGain':.75,'peakDBFS':peak(mix),'voiceMusicChecks':checks,'speechPlaybackRate':1,'sampleRate':sr,'channels':2}}
(out/'ASSET_ROLES.json').write_text(json.dumps(roles,indent=2));(q/'mix-report.md').write_text('# Mix verification\n\nOriginal keyboard score, no external samples. 48kHz stereo WAV. Speech playbackRate1.\n\n'+json.dumps(roles['mix'],indent=2)+'\n\nVoice duck is -18dB source gain, background -10dB, recovery0.5s. Global.75 gain applied after buses. S0 and S5 fully silent music.\n');np.save(q/'duck-gain.npy',gain);print('mix peak',peak(mix),checks)
