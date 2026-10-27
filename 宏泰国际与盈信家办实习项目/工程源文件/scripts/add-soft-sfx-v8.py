"""Audio-only, non-destructive SFX audition for the approved v7 picture.
Requires NumPy from the bundled workspace Python; does not call TTS or a network.
"""
from pathlib import Path
import subprocess,json,hashlib,wave,math,shutil
import numpy as np
ROOT=Path(__file__).resolve().parents[1];Q=ROOT/'qa/v8';Q.mkdir(parents=True,exist_ok=True)
ASSETS=ROOT/'public/sfx/v8';(ASSETS/'source').mkdir(parents=True,exist_ok=True)
LIB=Path('/Users/linwenbin/Desktop/codex工作流/视频样例/video-shotcraft-trial-2026-10-19/vendor/video-shotcraft/assets/audio')
SOURCE=ROOT/'out/BOI-HK_MiniMax粵語_首尾Logo動效_v7.mp4'
OUTPUT=ROOT/'out/BOI-HK_MiniMax粵語_輕音效試聽_v8.mp4'
if OUTPUT.exists():raise FileExistsError(f'Refusing to overwrite {OUTPUT}')
SR=48000;FPS=30
v7=json.loads((ROOT/'src/config/logo-hk-v7.json').read_text())
v6=json.loads((ROOT/'qa/v6/timing-plan.json').read_text())
N=v7['frames']*1600
def ff(args):return subprocess.check_output(['ffmpeg','-v','error','-nostdin',*map(str,args)])
def wav(path,x):
 with wave.open(str(path),'wb')as w:
  w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR)
  w.writeframes(np.rint(np.clip(x,-1,1)*32767).astype('<i2').tobytes())
def db(x):return 20*math.log10(max(float(np.max(abs(x))),1e-12))
specs={
 'tap-a':('text/typewriter-hit-soft.mp3',.095,.180,150,2700,.004,.035,'Typewriter soft hit',1366),
 'tap-b':('text/typewriter-hit-single.mp3',.130,.150,180,2400,.004,.035,'Mechanical typewriter single hit',1382),
 'paper':('paper/paper-page-turn.mp3',.020,.410,200,6500,.012,.075,'Page turn single',1104),
 'slide':('paper/paper-slide.mp3',.080,.660,180,6000,.018,.120,'Paper slide',1530),
 'air':('transition/sweep-fast-small.mp3',.055,.650,250,5500,.030,.140,'Fast small sweep transition',166),
}
assets={};records={}
for key,(rel,start,dur,hp,lp,fin,fout,name,item)in specs.items():
 src=LIB/'sfx'/rel;original=ASSETS/'source'/Path(rel).name
 if not original.exists():shutil.copy2(src,original)
 filters=f'atrim=start={start}:duration={dur},asetpts=PTS-STARTPTS,highpass=f={hp},lowpass=f={lp},afade=t=in:d={fin},afade=t=out:st={dur-fout}:d={fout}'
 raw=ff(['-i',original,'-af',filters,'-ar',SR,'-ac',2,'-f','f32le','-'])
 x=np.frombuffer(raw,dtype='<f4').reshape(-1,2).astype(np.float64)
 x/=max(float(np.max(abs(x))),1e-9)
 peak=int(np.argmax(np.max(abs(x),axis=1)))
 wav(ASSETS/f'{key}.wav',x*.9)
 # The mix uses the normalized float source, not the separately quantized WAV.
 assets[key]=x
 records[key]={'sourceFile':rel,'retainedSource':str(original.relative_to(ROOT)),
  'originalTitle':name,'sourceUrl':f'https://assets.mixkit.co/active_storage/sfx/{item}/{item}-preview.mp3',
  'licenseRecord':'Mixkit Sound Effects Free License, according to bundled ATTRIBUTION.md',
  'sourceSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'filters':filters,
  'durationSamples':len(x),'peakSample':peak,'peakFrames':peak/1600,
  'processedFile':str((ASSETS/f'{key}.wav').relative_to(ROOT))}
shutil.copy2(LIB/'ATTRIBUTION.md',ASSETS/'SOURCE_ATTRIBUTION.md')
(ASSETS/'PROVENANCE.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
shots={'S0':{'from':0,'frames':150}}
for s in v6['scenes'][1:]:shots[s['id']]={**s,'from':s['from']-102}
def mapped(sid,seconds):
 scene=shots[sid];start=scene['segments'][0]['sourceFrom'];f=start+seconds*FPS;cursor=0
 for seg in scene['segments']:
  if seg['sourceFrom']<=f<seg['sourceTo']:
   return cursor+(f-seg['sourceFrom'])/seg['rate']
  cursor+=seg['outputFrames']
 raise ValueError((sid,seconds,'target is outside the retained scene'))
cues=[]
def cue(sid,offset,key,level,label):
 offset=round(offset);target=shots[sid]['from']+offset;peak=records[key]['peakSample']
 start=target*1600-peak
 assert start>=0 and start+len(assets[key])<=N,(sid,label)
 cues.append({'scene':sid,'offsetFrames':offset,'targetPeakFrame':target,'source':key,
  'peakDBFSBeforeVoiceDuck':level,'label':label,'sourcePeakSample':peak,
  'startSample':start,'endSample':start+len(assets[key])})
for sid in ('S0','S7'):
 quiet=0 if sid=='S0' else -1.5
 cue(sid,22,'paper',-23+quiet,'Logo 底線展開')
 cue(sid,31,'tap-a',-23+quiet,'Logo 樹幹長出')
 for ring in range(6):
  offset=(3+ring*.55+.12)/(7/3)*FPS
  cue(sid,offset,'tap-a'if ring%2==0 else'tap-b',-24-ring*.65+quiet,f'Logo 第{ring+1}圈樹冠')
 cue(sid,100,'slide',-23+quiet,'中英字標由中心展開')
 cue(sid,108,'tap-b',-24+quiet,'完整品牌落定')
cue('S0',144,'air',-24,'片頭年輪退出')
for sid,s in shots.items():
 if sid not in ('S0','S1'):cue(sid,-2,'air',-24.5,'段落切換')
def native(sid,seconds,key,level,label):cue(sid,mapped(sid,seconds),key,level,label)
native('S1',13/30,'tap-a',-23,'第一行標題落定')
native('S1',.25+13/30,'tap-b',-25,'第二行標題落定')
native('S2',1.05,'slide',-25,'信任連線展開')
native('S2',1.3+13/30,'tap-a',-23.5,'值得信任的人落定')
native('S3',13/30,'tap-a',-25,'信任標題落定')
for i in (0,2,4,6):native('S3',.4+i*.32+.65,'paper',-27-i*.2,'年輪分層展開')
for i,start in enumerate((1.95,3.07,4.25)):
 native('S4',start+.15+13/30,'tap-a'if i%2==0 else'tap-b',-23.5,['合規','導師','系統'][i]+'圖標與字卡落定')
native('S5',13/30,'tap-a',-24,'立足香港標題落定')
native('S5',.9,'paper',-25,'香港天際線與根部展開')
for i,start in enumerate((.35,3.09,5.69)):
 native('S6',start+.3,'tap-a'if i%2==0 else'tap-b',-24.5,'季度成長資訊落定')
native('S6',6.39,'paper',-27,'第四圈年輪完成')
cues.sort(key=lambda c:c['targetPeakFrame'])
with wave.open(str(ROOT/'qa/v7/expected-audio.wav'),'rb')as w:
 assert w.getnchannels()==2 and w.getframerate()==SR and w.getnframes()==N
 voice=np.frombuffer(w.readframes(N),dtype='<i2').reshape(-1,2).astype(np.float64)/32768
# Gentle ducking applies to the SFX bus only. Narration remains at unity gain.
power=np.mean(voice**2,axis=1);window=SR//12
padded=np.pad(power,(window//2,window-window//2));cs=np.r_[0,np.cumsum(padded)]
rms=np.sqrt((cs[window:window+N]-cs[:N])/window)
duck=1-.32*np.clip((rms-.006)/.025,0,1)
sfx=np.zeros_like(voice)
for c in cues:
 x=assets[c['source']]*10**(c['peakDBFSBeforeVoiceDuck']/20)
 start,end=c['startSample'],c['endSample'];x=x*duck[start:end,None]
 # Very restrained stereo width; no hard panning or voice processing.
 sfx[start:end]+=x
 c['renderedPeakDBFS']=db(x)
 c['sampleAtDesignedPeak']=int(np.argmax(np.max(abs(assets[c['source']]),axis=1)))+start
mixed=voice+sfx
assert db(mixed)<-1,'Reduce SFX bus gain instead of compressing the narration'
wav(Q/'sfx-only.wav',sfx);wav(Q/'mix-reference.wav',mixed)
(Q/'cue-sheet.json').write_text(json.dumps({'fps':FPS,'sampleRate':SR,'frames':v7['frames'],
 'shots':{k:{'from':s['from'],'frames':s['frames']}for k,s in shots.items()},
 'narrationGain':1,'sfxDuckMinimum':.68,'cues':cues},ensure_ascii=False,indent=2))
ff(['-n','-i',SOURCE,'-i',Q/'mix-reference.wav','-map','0:v:0','-map','1:a:0',
 '-c:v','copy','-c:a','aac','-b:a','256k','-ar',SR,'-movflags','+faststart',OUTPUT])
report={'output':str(OUTPUT),'frames':v7['frames'],'nominalSeconds':v7['frames']/FPS,
 'events':len(cues),'voiceGain':1,'sfxPeakDBFS':db(sfx),'mixPeakDBFS':db(mixed),
 'videoOperation':'stream copy from approved v7','sha256':hashlib.sha256(OUTPUT.read_bytes()).hexdigest()}
(Q/'mix-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
