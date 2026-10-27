"""Prompt18 deterministic original additive score; no external samples or music."""
from pathlib import Path
import hashlib,json,subprocess,math
import numpy as np
R=Path(__file__).resolve().parents[1];Q=R/'qa/us-v1-60s-v5';M=R/'public/music/us-v2';SR=48000;N=60*SR
T=json.loads((R/'src/config/us-full-v3-timeline.json').read_text());SCENES=T['scenes'];time=np.arange(N)/SR

def db(value):return float(20*np.log10(max(float(value),1e-12)))
def peak(a):return db(np.max(np.abs(a)))
def rms(a):return float(np.sqrt(np.mean(np.asarray(a,dtype=np.float64)**2)))
def decode(path):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-ar',str(SR),'-ac','2','-f','f32le','-']),np.float32).reshape(-1,2)
def write(path,a):
 subprocess.run(['ffmpeg','-v','error','-f','f32le','-ar',str(SR),'-ac','2','-i','pipe:0','-c:a','pcm_s24le','-y',str(path)],input=np.asarray(a,dtype='<f4').tobytes(),check=True)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def smooth(x):return .5-.5*np.cos(np.pi*np.clip(x,0,1))
CHORDS=[('Am',[57,60,64],45),('F',[53,57,60],41),('C',[55,60,64],48),('G',[55,59,62],43)]
notes=[];chords=[]
for i,start in enumerate(np.arange(4,60,4.4)):
 name,pad,bass=CHORDS[i%4];start=round(float(start),6);chords.append(dict(time=start,chord=name,pad=pad,bass=bass,duration=4.8))
 for j,midi in enumerate(pad):notes.append(dict(time=start,midi=midi,duration=4.8,layer='pad',gainDB=-12,pan=[-.18,0,.18][j],chord=name,attack=1.2,release=.4))
 notes.append(dict(time=start,midi=bass,duration=4.8,layer='bass',gainDB=-8,pan=0,chord=name,attack=.14,release=.5))
 # Quiet octave doubling keeps the requested table bass and supplies 43.65/49 Hz
 # fundamentals on F/G. Both pitched notes are explicitly present in the score.
 notes.append(dict(time=start,midi=bass-12,duration=4.8,layer='bass',gainDB=-15,pan=0,chord=name,attack=.18,release=.5,subOctave=True))
melody=[(12.1,72,2.4),(14.7,76,2.4),(17.2,71,4.2),(19.5,74,2.4),(21.8,76,2.4),(24.4,72,3.2),(27,69,2.8),(29.4,72,3.2),(32,67,2.4),(35,74,2.4),(37.4,71,2.4),(53,67,3.2),(56.8,69,3.2)]
for i,(start,midi,duration) in enumerate(melody):notes.append(dict(time=start,midi=midi,duration=duration,layer='melody',gainDB=[0,-.6,-.3,.4][i%4],pan=[-.12,.08,.15,-.06][i%4],attack=.018,release=.2))
S3=SCENES[3]
for start in np.arange(S3['startFrame']/30+.6,S3['endFrame']/30,2*60/72):
 c=max((c for c in chords if c['time']<=start),key=lambda c:c['time']);notes.append(dict(time=round(float(start),6),midi=c['bass']-12,duration=1.1,layer='pulse',gainDB=-30,pan=0,attack=.14,release=.35,chord=c['chord']))
notes.sort(key=lambda n:(n['time'],n['layer'],n['midi']))
layers={key:np.zeros((N,2),np.float32) for key in ['pad','bass','melody','pulse']}
for i,note in enumerate(notes):
 start=round(note['time']*SR);length=min(round(note['duration']*SR),N-start)
 if length<=0:continue
 t=np.arange(length,dtype=np.float64)/SR;freq=440*2**((note['midi']-69)/12);layer=note['layer'];duration=note['duration']
 env=smooth(t/note['attack'])*smooth((duration-t)/note['release'])
 if layer=='melody':env*=.72*np.exp(-t/2.2)+.28*np.exp(-t/.25)
 if layer=='pulse':env*=np.exp(-t/.7)
 # Slow keyboard pad, round bass and a soft struck-keyboard melody: only sines.
 weights=([1,.14,.035] if layer=='melody' else [1,.07,.02] if layer=='pad' else [1,.12,.025] if not note.get('subOctave') else [1])
 pan=note['pan'];gain=10**(note['gainDB']/20)
 for channel in range(2):
  detune=(1+(.00012 if channel else -.00012)) if layer=='pad' else 1
  wave=sum(weight*np.sin(2*np.pi*freq*(h+1)*detune*t) for h,weight in enumerate(weights))/sum(weights)
  panning=math.sqrt((1+(pan if channel else -pan))/2)
  layers[layer][start:start+length,channel]+=(wave*env*gain*panning).astype(np.float32)
# Section masks and relative layer balance, including intentional hard music silence.
levelDB={'S0':-240,'S1':-20,'S2':-16,'S3':-13,'S4':-16,'S5':-18,'S6':-240,'S7':-16}
layerBalance={
 'S0':[0,0,0,0], 'S1':[1,.8,0,0], 'S2':[1.2,1,1,0], 'S3':[1.45,1.2,1.1,1],
 'S4':[1.2,.9,.7,0], 'S5':[.85,.75,0,0], 'S6':[0,0,0,0], 'S7':[1,.9,1,0]}
layerNames=['pad','bass','melody','pulse'];masks={k:np.zeros(N,np.float32) for k in layerNames};bedDB=np.full(N,-240.,np.float32)
for s in SCENES:
 a=s['startFrame']*1600;b=s['endFrame']*1600
 bedDB[a:b]=levelDB[s['id']]
 for j,key in enumerate(layerNames):
  value=layerBalance[s['id']][j];masks[key][a:b]=value
  # Melody entry/withdrawal softens over 0.2 s inside its allowed scene only.
  if key=='melody' and value:
   fade=min(int(.2*SR),b-a);masks[key][a:a+fade]*=smooth(np.linspace(0,1,fade));masks[key][b-fade:b]*=smooth(np.linspace(1,0,fade))
  if key=='pulse' and value:
   fade=int(.25*SR);masks[key][a:a+fade]*=smooth(np.linspace(0,1,fade));masks[key][b-fade:b]*=smooth(np.linspace(1,0,fade))
# 80 ms section gain ramps at musical changes, with full gates at S0/S6 boundaries.
for s in SCENES[1:]:
 a=s['startFrame']*1600
 if s['id'] not in ['S1','S6','S7']:
  r=int(.08*SR);previous=bedDB[a-1];bedDB[a:a+r]=previous+(levelDB[s['id']]-previous)*smooth(np.linspace(0,1,r))
shaped=sum(layers[k]*masks[k][:,None] for k in layerNames)
normalization=.70/max(np.max(np.abs(shaped)),1e-12);shaped*=normalization
# Historical mix used -18 dB as an absolute source target, not an extra -18 dB
# after its bed level. Keep that convention and its 0.5 s recovery.
duckDB=bedDB.copy()
for s in SCENES:
 a=s['voiceStartFrame']*1600;b=a+round(s['duration']*SR);b=min(N,b)
 target=np.minimum(bedDB[a:b],-18);duckDB[a:b]=np.minimum(duckDB[a:b],target)
 pre=max(s['startFrame']*1600,a-int(.12*SR))
 if pre<a:duckDB[pre:a]=np.minimum(duckDB[pre:a],np.linspace(bedDB[pre],min(levelDB[s['id']],-18),a-pre))
 post=min(s['endFrame']*1600,b+int(.5*SR))
 if post>b:duckDB[b:post]=np.minimum(duckDB[b:post],np.linspace(min(levelDB[s['id']],-18),levelDB[s['id']],post-b))
# A brief level swell at the word "nine"; no pitch sweep/noise/riser added.
s=SCENES[4];word=next(w for w in s['words'] if w['word'].strip().lower()=='nine');nine=(s['voiceStartFrame']+math.ceil(word['start']*30))/30
swell=np.zeros(N,np.float32);a=round(nine*SR);count=round(.6*SR);swell[a:a+count]=3*np.sin(np.linspace(0,np.pi,count))**2
# Fade into/out of intentional music-only silence, and resolve the last 1.5 sec.
fade=np.ones(N,np.float32);fade[:SCENES[0]['endFrame']*1600]=0
s6a=SCENES[6]['startFrame']*1600;s6b=SCENES[6]['endFrame']*1600;fade[s6a:s6b]=0
fade[4*SR:4*SR+int(.4*SR)]*=smooth(np.linspace(0,1,int(.4*SR)))
fade[s6a-int(.15*SR):s6a]*=smooth(np.linspace(1,0,int(.15*SR)))
fade[s6b:s6b+int(.5*SR)]*=smooth(np.linspace(0,1,int(.5*SR)))
fade[-int(1.5*SR):]*=smooth(np.linspace(1,0,int(1.5*SR)))
bed=shaped*(10**((bedDB+swell)/20)*fade)[:,None]
music=shaped*(10**((duckDB+swell)/20)*fade)[:,None]
voice=decode(R/'qa/us-v1-60s-v2/voice-bus.wav');assert len(voice)==N
mix=voice+music
assert peak(mix)<=-1,peak(mix)
assert np.max(np.abs(music[:4*SR]))==0 and np.max(np.abs(music[s6a:s6b]))==0
M.mkdir(exist_ok=True);write(M/'original-score-v2.wav',bed);write(M/'full-review-mix-v5.wav',mix)
write(Q/'music/music-bus.wav',music);write(Q/'music/score-pre-automation.wav',shaped)
# Exact existing PCM voice bus is reused; this file is a byte-preserving copy.
(Q/'music/voice-bus.wav').write_bytes((R/'qa/us-v1-60s-v2/voice-bus.wav').read_bytes())
np.save(Q/'music/duck-db.npy',duckDB);np.save(Q/'music/fade.npy',fade)
# Active voices are counted from the actual note envelopes and section masks.
probeTimes=np.arange(0,60,.01);poly=np.zeros(len(probeTimes),np.int32)
for note in notes:
 elapsed=probeTimes-note['time'];valid=(elapsed>=0)&(elapsed<note['duration']);idx=np.flatnonzero(valid)
 if len(idx)==0:continue
 env=smooth(elapsed[idx]/note['attack'])*smooth((note['duration']-elapsed[idx])/note['release'])
 if note['layer']=='melody':env*=.72*np.exp(-elapsed[idx]/2.2)+.28*np.exp(-elapsed[idx]/.25)
 if note['layer']=='pulse':env*=np.exp(-elapsed[idx]/.7)
 sample=np.minimum(N-1,(probeTimes[idx]*SR).astype(int));effective=env*masks[note['layer']][sample]*(10**(note['gainDB']/20))*fade[sample]
 poly[idx]+=effective>.001
np.save(Q/'music/polyphony.npy',poly)
def bandEnergy(data):
 mono=data.mean(axis=1);window=np.hanning(SR);total=0;count=0;freq=np.fft.rfftfreq(SR,1/SR);sel=(freq>=40)&(freq<=50)
 for start in range(0,len(mono)-SR+1,SR//2):
  spectrum=np.fft.rfft(mono[start:start+SR]*window);total+=float(np.sum(np.abs(spectrum[sel])**2)/np.sum(window**2)/SR);count+=1
 return total/count
oldMusic=decode(R/'qa/us-v1-60s-v2/music-bus.wav');oldBand=bandEnergy(oldMusic);newBand=bandEnergy(music)
checks=[]
for s in SCENES:
 a=s['startFrame']*1600;b=s['endFrame']*1600;va=s['voiceStartFrame']*1600;vb=min(N,va+round(s['duration']*SR))
 checks.append(dict(scene=s['id'],musicRMSDBFS=db(rms(music[a:b])),musicPeakDBFS=peak(music[a:b]),voicePeakDBFS=peak(voice[va:vb]),duringVoiceSeparationDB=peak(voice[va:vb])-peak(music[va:vb])))
s3=next(c for c in checks if c['scene']=='S3');s5=next(c for c in checks if c['scene']=='S5')
report=dict(scoreNotes=len(notes),polyphonyMeanFull60s=float(poly.mean()),polyphonyMeanMusicOnly=float(poly[poly>0].mean()),polyphonyMax=int(poly.max()),bass40to50EnergyGainDB=float(10*np.log10(newBand/max(oldBand,1e-30))),oldBandEnergy=oldBand,newBandEnergy=newBand,S3minusS5RMSDB=s3['musicRMSDBFS']-s5['musicRMSDBFS'],melodyDurations=sorted(set(n['duration'] for n in notes if n['layer']=='melody')),mixPeakDBFS=peak(mix),musicPeakDBFS=peak(music),voicePeakDBFS=peak(voice),voiceBusByteIdentical=True,nineSwellStart=nine,sceneChecks=checks)
assert report['polyphonyMeanFull60s']>=3,report
assert report['bass40to50EnergyGainDB']>=6,report
assert report['S3minusS5RMSDB']>=5,report
assert min(c['duringVoiceSeparationDB'] for c in checks)>=12,report
assert peak(voice)-peak(music)>=12,report
roles=json.loads((M/'ASSET_ROLES.json').read_text())
roles['scoreV2']=dict(status='original_project_additive_score',source='original-score-v2.wav',mix='full-review-mix-v5.wav',sampleRate=SR,channels=2,encoding='24-bit PCM WAV',externalSamples=False,externalComposition=False,instruments=['additive soft keyboard melody','sine keyboard pad','rounded tonal bass with explicitly scored sub-octave doubling','tonal bass pulse'],excluded=['drum kit','strings','riser'],score=notes,chords=chords,chordHopSeconds=4.4,chordDurationSeconds=4.8,chordOverlapSeconds=.4,chordCyclesIn60Seconds=len(chords)/4,sectionGainDB=levelDB,sectionLayerBalance=layerBalance,normalizationGain=float(normalization),voiceDuckAbsoluteSourceDB=-18,recoverySeconds=.5,nineStateSwell=dict(start=nine,duration=.6,gainDB=3,type='amplitude only'),fadeOutSeconds=1.5,voiceSource='qa/us-v1-60s-v2/voice-bus.wav',voiceSourceSha256=sha(Q/'music/voice-bus.wav'),sourceAssetSha256=sha(M/'original-score-v2.wav'),mixSha256=sha(M/'full-review-mix-v5.wav'),measurement=report,adaptations=['4.8s hold with .4s overlap implies 4.4s hop: 13 chord events / 3.25 cycles fit the 60s film, not 15 four-chord cycles.','Keep all requested table pitches; explicitly score quiet sub-octave bass notes to supply 40-50Hz energy.','Duck -18dB retains historical absolute-source semantics; not an additional -18 after section gain.','Original 42-note metadata spans over 150s, not 60s; preserve restrained keyboard idea, reharmonize and vary durations for this timeline.'])
(M/'ASSET_ROLES.json').write_text(json.dumps(roles,ensure_ascii=False,indent=2)+'\n')
(Q/'music/analysis.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(Q/'music/score.json').write_text(json.dumps(roles['scoreV2'],ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
