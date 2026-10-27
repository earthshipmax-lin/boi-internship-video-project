from pathlib import Path
import json,subprocess,hashlib,wave,math
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];Q=ROOT/'qa/v9'
V7=ROOT/'out/BOI-HK_MiniMax粵語_首尾Logo動效_v7.mp4'
V8=ROOT/'out/BOI-HK_MiniMax粵語_物件音效與柔和年輪_v9.mp4'
def ff(args):return subprocess.check_output(['ffmpeg','-v','error','-nostdin',*map(str,args)])
def read(path):
 with wave.open(str(path),'rb')as w:
  assert w.getframerate()==48000 and w.getnchannels()==2
  return np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,2).astype(float)/32768
def db(x):return 20*math.log10(max(float(np.max(abs(x))),1e-12))
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(V8)]))
video=next(s for s in probe['streams']if s['codec_type']=='video');assert int(video['nb_frames'])==1394
ff(['-i',V8,'-f','null','-'])
def frame_hashes(path):
 raw=ff(['-i',path,'-map','0:v','-an','-f','framemd5','-']).decode()
 return [l.rsplit(',',1)[-1].strip()for l in raw.splitlines()if not l.startswith('#')]
before,after=frame_hashes(V7),frame_hashes(V8);assert before==after and len(after)==1394
base=json.loads((Q/'baseline-hashes.json').read_text())
changed=[p for p,h in base.items()if hashlib.sha256((ROOT.parent/p).read_bytes()).hexdigest()!=h]
assert not changed,changed
ff(['-y','-i',V8,'-map','0:a:0','-acodec','pcm_s16le',Q/'output-audio.wav'])
x=read(Q/'mix-reference.wav');y=read(Q/'output-audio.wav');n=len(x)
voice=read(ROOT/'qa/v7/expected-audio.wav');sfx=read(Q/'sfx-only.wav')
corr=float(np.corrcoef(x.reshape(-1),y[:n].reshape(-1))[0,1]);assert corr>.9999
residual=x-sfx-voice;maxerr=float(np.max(abs(residual)));assert maxerr<=2/32768
sheet=json.loads((Q/'cue-sheet.json').read_text());probes=[]
for target in (22,31,42,144,686,938):
 c=next(c for c in sheet['cues']if c['targetPeakFrame']==target and (target!=938 or c['family']=='title'))
 source=read(ROOT/f"public/sfx/v9/{c['source']}.wav").mean(axis=1)
 start=c['startSample'];pad=320
 actual=(y[:n]-voice)[start-pad:start+len(source)+pad].mean(axis=1)
 cc=np.correlate(actual,source,mode='valid');offset=int(np.argmax(cc))-pad
 assert abs(offset)<=800,(target,offset)
 probes.append({'scene':c['scene'],'targetPeakFrame':target,'source':c['source'],'offsetSamples':offset,'offsetFrames':offset/1600})
# Decode picture samples at actual SFX anchor times, rather than only copying
# old visual QA files; the whole-picture hash comparison above remains primary.
selected=[next(c for c in sheet['cues']if c['targetPeakFrame']==42),next(c for c in sheet['cues']if c['scene']=='S3'and c['family']=='ring'),*[next(c for c in sheet['cues']if c['label'].startswith(name)and c['family']=='title')for name in ('合規','導師','系統')],next(c for c in sheet['cues']if c['scene']=='S5'and c['family']=='object')]
actual=Q/'actual';actual.mkdir(exist_ok=True);canvas=Image.new('RGB',(1440,600),(235,232,225));draw=ImageDraw.Draw(canvas)
for i,c in enumerate(selected):
 f=c['targetPeakFrame'];p=actual/f'cue-f{f}.png'
 ff(['-y','-i',V8,'-vf',f'select=eq(n\\,{f})','-frames:v',1,p])
 im=Image.open(p).convert('RGB');im.thumbnail((480,270));left=(i%3)*480;top=(i//3)*300
 canvas.paste(im,(left,top));draw.text((left+8,top+275),f"{c['scene']} {c['source']} f{f} ({f/30:.2f}s)",fill='black')
canvas.save(Q/'cue-contact.jpg')
old=json.loads((ROOT/'qa/v8/cue-sheet.json').read_text())['cues']
transitionChanges=[]
for c in sheet['cues']:
 if c['family']=='transition':
  prior=next(p for p in old if p['scene']==c['scene']and p['targetPeakFrame']==c['targetPeakFrame']and p['source']=='air')
  transitionChanges.append({'scene':c['scene'],'targetPeakFrame':c['targetPeakFrame'],'designChangeDB':c['peakDBFSBeforeVoiceDuck']-prior['peakDBFSBeforeVoiceDuck'],'renderedPeakChangeDB':c['renderedPeakDBFS']-prior['renderedPeakDBFS']})
assert all(abs(c['designChangeDB']+9)<.001 for c in transitionChanges)
assert all(c['renderedPeakChangeDB']<-7 for c in transitionChanges)
titleChanges=[]
for c in sheet['cues']:
 if c['family']=='title'and c['scene']not in ('S0','S7'):
  prior=next((p for p in old if p['scene']==c['scene']and p['targetPeakFrame']==c['targetPeakFrame']and p['source']in('tap-a','tap-b')),None)
  if prior:titleChanges.append({'scene':c['scene'],'targetPeakFrame':c['targetPeakFrame'],
   'peakIncreaseDB':c['renderedPeakDBFS']-prior['renderedPeakDBFS'],'oldSource':prior['source'],'newSource':c['source']})
assert len(titleChanges)>=9 and min(c['peakIncreaseDB']for c in titleChanges)>4
assert set(c['scene']for c in sheet['cues']if c['family']=='title')==set('S'+str(i)for i in range(8))
nonzero=np.flatnonzero(np.max(abs(sfx),axis=1)>1/32768)
report={'frames':1394,'videoFrameHashesIdenticalToV7':len(after),'fullDecode':'PASS',
 'videoDuration':float(video['duration']),'containerDuration':float(probe['format']['duration']),
 'allBaselineFilesUnchanged':len(base),'narrationGain':1,'narrationResidualMaxErrorLSB':maxerr*32768,
 'mixCorrelationToReferencePCM':corr,'decodedPeakDBFS':db(y),'sfxOnlyPeakDBFS':db(sfx),
 'sfxEventCount':len(sheet['cues']),'transitionChangesDB':transitionChanges,'allEightScenesHaveTitleSFX':True,
 'matchedContentTitlePeakIncreasesDB':titleChanges,'outputAlignmentProbes':probes,
 'lastSfxSeconds':float(nonzero[-1]/48000),'lastSecondSfxSilent':bool(not np.any(sfx[-48000:])),
 'decodedAudioSamples':len(y),'referenceAudioSamples':n,
 'sha256':hashlib.sha256(V8.read_bytes()).hexdigest(),
 'subjectiveLimit':'No supported audio-input audition available; loudness, tone and liveliness await user listening.'}
(Q/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
