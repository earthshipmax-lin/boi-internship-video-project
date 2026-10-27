"""v9 object-specific, warmer SFX; lower transitions, preserve approved picture/VO.
Uses local source files and deterministic modal synthesis. No network or TTS.
Run with workspace Python containing NumPy. Existing output is never overwritten.
"""
from pathlib import Path
import json,subprocess,wave,hashlib,math,shutil
import numpy as np
ROOT=Path(__file__).resolve().parents[1];Q=ROOT/'qa/v9';Q.mkdir(parents=True,exist_ok=True)
A=ROOT/'public/sfx/v9';(A/'source').mkdir(parents=True,exist_ok=True)
LIB=Path('/Users/linwenbin/Desktop/codex工作流/视频样例/video-shotcraft-trial-2026-10-19/vendor/video-shotcraft/assets/audio')
SOURCE=ROOT/'out/BOI-HK_MiniMax粵語_首尾Logo動效_v7.mp4'
OUTPUT=ROOT/'out/BOI-HK_MiniMax粵語_物件音效與柔和年輪_v9.mp4'
if OUTPUT.exists():raise FileExistsError(OUTPUT)
SR=48000;FPS=30;N=1394*1600
def ff(args):return subprocess.check_output(['ffmpeg','-v','error','-nostdin',*map(str,args)])
def read(p):
 with wave.open(str(p),'rb')as w:
  assert w.getframerate()==SR and w.getnchannels()==2
  return np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,2).astype(float)/32768
def wav(p,x):
 with wave.open(str(p),'wb')as w:
  w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR)
  w.writeframes(np.rint(np.clip(x,-1,1)*32767).astype('<i2').tobytes())
def db(x):return 20*math.log10(max(float(np.max(abs(x))),1e-12))
assets={};provenance={}
def store(key,x,meta):
 if x.ndim==1:x=np.column_stack((x,x))
 x=x/max(float(np.max(abs(x))),1e-9)
 assets[key]=x;peak=int(np.argmax(np.max(abs(x),axis=1)))
 wav(A/f'{key}.wav',x*.9)
 provenance[key]={**meta,'processedFile':str((A/f'{key}.wav').relative_to(ROOT)),
  'peakSample':peak,'durationSamples':len(x),'peakFrames':peak/1600}
for key in ('paper','slide','air'):
 p=ROOT/f'public/sfx/v8/{key}.wav'
 meta=json.loads((ROOT/'public/sfx/v8/PROVENANCE.json').read_text())[key]
 store(key,read(p),{**meta,'derivedFromV8':str(p.relative_to(ROOT))})
for key,rel,start,duration,hp,lp,item,name in [
 ('system','mech/lock-quick.mp3',0,.240,160,1900,2854,'Quick lock sound'),
 ('pencil','text/pencil-write-short.mp3',.200,.550,200,3400,2376,'Short pencil writing')]:
 src=LIB/'sfx'/rel;retained=A/'source'/src.name;shutil.copy2(src,retained)
 fade=.065
 filters=f'atrim=start={start}:duration={duration},asetpts=PTS-STARTPTS,highpass=f={hp},lowpass=f={lp},afade=t=in:d=0.006,afade=t=out:st={duration-fade}:d={fade}'
 x=np.frombuffer(ff(['-i',src,'-af',filters,'-ar',SR,'-ac',2,'-f','f32le','-']),dtype='<f4').reshape(-1,2).astype(float)
 store(key,x,{'sourceFile':rel,'retainedSource':str(retained.relative_to(ROOT)),
  'originalTitle':name,'sourceUrl':f'https://assets.mixkit.co/active_storage/sfx/{item}/{item}-preview.mp3',
  'sourceSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'filters':filters,
  'licenseRecord':'Mixkit SFX Free License according to existing bundled ATTRIBUTION.md'})
# Original restrained struck-wood models: a soft attack and rapidly damped
# inharmonic partials, not a sustained oscillator / notification tone.
def struck(freq,duration=.48,decay=.15,seed=9):
 t=np.arange(round(duration*SR))/SR
 signal=sum(weight*np.sin(2*np.pi*freq*ratio*t)*np.exp(-t/(decay/fall))
  for ratio,weight,fall in ((1,1,1),(2.756,.19,2.3),(5.404,.045,4.5)))
 attack=np.minimum(t/.009,1);attack=np.sin(attack*np.pi/2)**2
 noise=np.random.default_rng(seed).standard_normal(len(t))
 noise=np.convolve(noise,np.ones(13)/13,mode='same')*.05*np.exp(-t/.008)
 end=np.clip((duration-t)/.07,0,1)**2
 return (signal+noise)*attack*end
store('felt',struck(185,.170,.043),{'kind':'original deterministic DSP','role':'cushioned title landing','frequency':185,'attackSeconds':.009,'seed':9})
store('shield',struck(220,.230,.070),{'kind':'original deterministic DSP','role':'rounded shield knock','frequency':220,'attackSeconds':.009,'seed':9})
left=struck(245,.250,.060);right=struck(294,.210,.050)
pair=left.copy();offset=round(.045*SR);pair[offset:]+=right[:len(pair)-offset]*.56
store('join',pair,{'kind':'original deterministic DSP','role':'two dots joining / mentor response','frequencies':[245,294],'secondStrikeSeconds':.045,'seed':9})
notes=[('C4',261.625565),('D4',293.664768),('E4',329.627557),('G4',391.995436),('A4',440.),('C5',523.251131),('D5',587.329536)]
for name,freq in notes:
 store(f'ring-{name}',struck(freq,.580,.170),{'kind':'original deterministic DSP',
  'role':'soft wooden mallet, major pentatonic ring growth','note':name,'frequency':freq,
  'partials':[1,2.756,5.404],'partialWeights':[1,.19,.045],'attackSeconds':.009,'seed':9})
shutil.copy2(LIB/'ATTRIBUTION.md',A/'SOURCE_ATTRIBUTION.md')
(A/'PROVENANCE.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2))
v6=json.loads((ROOT/'qa/v6/timing-plan.json').read_text());shots={'S0':{'from':0,'frames':150}}
for s in v6['scenes'][1:]:shots[s['id']]={**s,'from':s['from']-102}
def mapped(sid,seconds):
 scene=shots[sid];f=scene['segments'][0]['sourceFrom']+seconds*FPS;cursor=0
 for seg in scene['segments']:
  if seg['sourceFrom']<=f<seg['sourceTo']:return cursor+(f-seg['sourceFrom'])/seg['rate']
  cursor+=seg['outputFrames']
 raise ValueError((sid,seconds))
cues=[]
def cue(sid,offset,key,level,label,family):
 offset=round(offset);target=shots[sid]['from']+offset;peak=provenance[key]['peakSample'];start=target*1600-peak
 assert start>=0 and start+len(assets[key])<=N,(sid,label)
 cues.append({'scene':sid,'offsetFrames':offset,'targetPeakFrame':target,'source':key,
  'family':family,'peakDBFSBeforeVoiceDuck':level,'label':label,
  'sourcePeakSample':peak,'startSample':start,'endSample':start+len(assets[key])})
def native(sid,t,key,level,label,family):cue(sid,mapped(sid,t),key,level,label,family)
tree=json.loads((ROOT/'src/assets/tree.json').read_text())
for sid in ('S0','S7'):
 quiet=0 if sid=='S0' else -1.5
 cue(sid,22,'paper',-24+quiet,'Logo 底線展開','logo')
 cue(sid,31,'shield',-22+quiet,'Logo 樹幹長出','object')
 for i in range(6):
  first=min(3+i*.55+abs(90-l['deg'])/110*.45 for l in tree['LEAF_CONTOURS']if l['ring']==i)
  cue(sid,(first+.16)/(7/3)*FPS,'ring-'+notes[i][0],-24-i*.45+quiet,f'Logo 第{i+1}圈樹冠','ring')
 cue(sid,100,'slide',-25+quiet,'中英字標中心展開','logo')
 cue(sid,108,'felt',-20.5+quiet,'完整品牌落定','title')
cue('S0',144,'air',-33,'片頭年輪退出','transition')
for sid in shots:
 if sid not in ('S0','S1'):cue(sid,-2,'air',-33.5,'段落切換','transition')
native('S1',13/30,'felt',-18,'全球最大標題落定','title')
native('S1',.25+13/30,'felt',-20,'跨境財富管理標題落定','title')
native('S2',1.05,'join',-21,'信任兩點連接','object')
native('S2',1.3+13/30,'join',-18.5,'值得信任的人標題落定','title')
native('S3',13/30,'felt',-19,'信任標題落定','title')
native('S3',.4+13/30,'felt',-21,'一圈一圈長出來標題落定','title')
for i in range(7):native('S3',.4+i*.32+.65,'ring-'+notes[i][0],-23-i*.25,f'第{i+1}圈年輪柔和上行','ring')
for i,(start,key,name)in enumerate(zip((1.95,3.07,4.25),('shield','join','system'),('合規','導師','系統'))):
 native('S4',start+.25,key,-21.5,name+'圖形描出','object')
 native('S4',start+.15+13/30,key,-18.5,name+'標題與物件落定','title')
native('S5',13/30,'felt',-18.5,'立足香港標題落定','title')
native('S5',.36,'pencil',-21,'香港天際線描出','object')
native('S5',.72,'pencil',-24,'根部向兩側延伸','object')
for i,start in enumerate((.35,3.09,5.69)):
 native('S6',start+.3,'felt',-20.5,'季度成長資訊落定','title')
 native('S6',start+.25,'ring-'+['C4','E4','G4'][i],-22,'季度對應年輪展開','ring')
native('S6',6.39,'ring-C5',-23,'第四圈年輪完成','ring')
native('S7',.3+13/30,'felt',-20,'歡迎語標題落定','title')
cues.sort(key=lambda c:c['targetPeakFrame'])
voice=read(ROOT/'qa/v7/expected-audio.wav');assert len(voice)==N
power=np.mean(voice**2,axis=1);win=SR//12;pad=np.pad(power,(win//2,win-win//2));cs=np.r_[0,np.cumsum(pad)]
rms=np.sqrt((cs[win:win+N]-cs[:N])/win)
# Content sounds remain more present; transitions stay much quieter.
duck=1-.18*np.clip((rms-.006)/.025,0,1)
sfx=np.zeros_like(voice);transitions=np.zeros_like(voice);content=np.zeros_like(voice)
for c in cues:
 start,end=c['startSample'],c['endSample'];x=assets[c['source']]*10**(c['peakDBFSBeforeVoiceDuck']/20)*duck[start:end,None]
 sfx[start:end]+=x
 (transitions if c['family']=='transition'else content)[start:end]+=x
 c['renderedPeakDBFS']=db(x)
mixed=voice+sfx;assert db(mixed)<-1,'Adjust SFX gain, never limit the narration'
for name,x in [('sfx-only',sfx),('transition-only',transitions),('content-only',content),('mix-reference',mixed)]:wav(Q/f'{name}.wav',x)
(Q/'cue-sheet.json').write_text(json.dumps({'fps':FPS,'sampleRate':SR,'frames':1394,
 'narrationGain':1,'sfxDuckMinimum':.82,'shots':{k:{'from':s['from'],'frames':s['frames']}for k,s in shots.items()},
 'cues':cues},ensure_ascii=False,indent=2))
ff(['-n','-i',SOURCE,'-i',Q/'mix-reference.wav','-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','256k','-ar',SR,'-movflags','+faststart',OUTPUT])
report={'output':str(OUTPUT),'frames':1394,'nominalSeconds':1394/30,'events':len(cues),
 'transitionChangeDB':-9,'contentTitleChangeDB':'approximately +5 to +7, with softened material-specific timbres',
 'voiceGain':1,'sfxPeakDBFS':db(sfx),'transitionPeakDBFS':db(transitions),'mixPeakDBFS':db(mixed),
 'sha256':hashlib.sha256(OUTPUT.read_bytes()).hexdigest()}
(Q/'mix-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
