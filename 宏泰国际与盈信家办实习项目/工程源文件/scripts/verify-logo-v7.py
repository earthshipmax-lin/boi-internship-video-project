from pathlib import Path
import json,subprocess,wave,hashlib,math
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];Q=ROOT/'qa/v7'
V7=ROOT/'out/BOI-HK_MiniMax粵語_首尾Logo動效_v7.mp4'
V6=ROOT/'out/BOI-HK_MiniMax粵語_快轉場自然語速_v6.mp4'
timing=json.loads((ROOT/'src/config/logo-hk-v7.json').read_text())
def ff(args):return subprocess.check_output(['ffmpeg','-v','error','-nostdin',*args])
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(V7)]))
v=next(s for s in probe['streams']if s['codec_type']=='video')
a=next(s for s in probe['streams']if s['codec_type']=='audio')
assert int(v['nb_frames'])==timing['frames']
assert v['width']==1920 and v['height']==1080 and v['r_frame_rate']=='30/1'
ff(['-i',str(V7),'-f','null','-'])
def hashes(file):
 raw=ff(['-i',str(file),'-map','0:v:0','-an','-f','framemd5','-']).decode()
 return [line.rsplit(',',1)[-1].strip()for line in raw.splitlines()if not line.startswith('#')]
old,new=hashes(V6),hashes(V7)
oldbody=old[252:1300];newbody=new[150:1198]
assert len(newbody)==1048 and newbody==oldbody,'Body frame pixels differ from v6'
ff(['-y','-i',str(V7),'-map','0:a:0','-acodec','pcm_s16le',str(Q/'output-audio.wav')])
def samples(p):
 with wave.open(str(p),'rb')as w:return np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float64),w.getnchannels(),w.getframerate()
x,nc,sr=samples(Q/'expected-audio.wav');y,ny,sy=samples(Q/'output-audio.wav')
assert nc==ny and sr==sy==48000
size=min(len(x),len(y));corr=float(np.corrcoef(x[:size],y[:size])[0,1]);assert corr>.9999
base=json.loads((Q/'baseline-hashes.json').read_text());changed=[]
for name,h in base.items():
 p=ROOT.parent/name
 if hashlib.sha256(p.read_bytes()).hexdigest()!=h:changed.append(name)
assert changed==['video/src/Root.tsx'],changed
actual=Q/'actual';actual.mkdir(exist_ok=True)
picks=[('intro-growth',66),('intro-complete',126),('S1',283),('S2',421),('S3',606),('S4',809),('S5',909),('S6',1182),('outro-trunk',1198+36),('outro-leaves',1198+66),('outro-complete',1198+132),('final',1393)]
for name,frame in picks:
 ff(['-y','-i',str(V7),'-vf',f'select=eq(n\\,{frame})','-frames:v','1',str(actual/f'{name}.png')])
canvas=Image.new('RGB',(1440,math.ceil(len(picks)/3)*300),(235,232,225));draw=ImageDraw.Draw(canvas)
for i,(name,frame)in enumerate(picks):
 im=Image.open(actual/f'{name}.png').convert('RGB');im.thumbnail((480,270));left=(i%3)*480;top=(i//3)*300
 canvas.paste(im,(left,top));draw.text((left+10,top+275),f'{name}: f{frame} ({frame/30:.2f}s)',fill='black')
canvas.save(Q/'actual-contact.jpg')
native=np.asarray(Image.open(Q/'outro-f165.png').convert('RGB')).astype(float)
final=np.asarray(Image.open(actual/'final.png').convert('RGB')).astype(float)
report={'frames':len(new),'duration':float(v['duration']),'containerDuration':float(probe['format']['duration']),
 'video':{k:v.get(k)for k in ['codec_name','profile','pix_fmt','width','height','r_frame_rate','time_base','color_range','color_space']},
 'audio':{k:a.get(k)for k in ['codec_name','sample_rate','channels','duration']},
 'fullDecode':'PASS','bodyDecodedFramesIdenticalToV6':len(newbody),'bodyFrameHashesMatch':newbody==oldbody,
 'audioCorrelationToUnchangedV6PCM':corr,'audioPeakDBFS':20*math.log10(float(np.max(np.abs(y)))/32768),
 'expectedPCMFrames':len(x)//nc,'decodedAudioFrames':len(y)//nc,
 'outroFinalRGBMeanAbsoluteErrorToNative':float(np.abs(native-final).mean()),
 'baselineFiles':len(base),'unchangedBaselineFiles':len(base)-len(changed),
 'intentionalExistingSourceChange':changed,'nativeIntroSeconds':5,'logoCompleteSeconds':3.6,
 'introStableBrandSeconds':1,'outroStableBrandSeconds':(196-108)/30,
 'sha256':hashlib.sha256(V7.read_bytes()).hexdigest(),'actualKeyframes':dict(picks)}
(Q/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
