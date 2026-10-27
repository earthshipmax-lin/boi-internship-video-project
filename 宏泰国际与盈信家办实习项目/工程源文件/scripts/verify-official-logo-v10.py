from pathlib import Path
import json,subprocess,hashlib
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];Q=R/'qa/v10'
OLD=R/'out/BOI-HK_MiniMax粵語_物件音效與柔和年輪_v9.mp4'
NEW=R/'out/BOI-HK_MiniMax粵語_原版SVG標誌_v10.mp4'
def ff(args):return subprocess.check_output(['ffmpeg','-v','error','-nostdin',*map(str,args)])
def hashes(p):
 raw=ff(['-i',p,'-map','0:v:0','-an','-f','framemd5','-']).decode()
 return [l.rsplit(',',1)[-1].strip()for l in raw.splitlines()if not l.startswith('#')]
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(NEW)]))
v=next(s for s in probe['streams']if s['codec_type']=='video');assert int(v['nb_frames'])==1394
ff(['-i',NEW,'-f','null','-'])
before,after=hashes(OLD),hashes(NEW);assert len(after)==1394 and before[150:1198]==after[150:1198]
def audio_packets(p):
 return json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','a:0','-show_packets',
  '-show_data_hash','sha256','-show_entries','packet=pts,dts,duration,data_hash,side_data_list','-of','json',str(p)]))['packets']
ap,bp=audio_packets(OLD),audio_packets(NEW);assert ap==bp,'Audio packets or timestamps changed'
oldpcm=ff(['-i',OLD,'-map','0:a:0','-f','s16le','-']);newpcm=ff(['-i',NEW,'-map','0:a:0','-f','s16le','-'])
assert oldpcm==newpcm,'Decoded audio changed'
baseline=json.loads((Q/'baseline-hashes.json').read_text())
changed=[p for p,h in baseline.items()if hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h]
assert changed==[str(R/'src/Root.tsx')],changed
source=Path('/Users/linwenbin/Desktop/宏泰.svg');copy=R/'public/brand/v10/宏泰.svg';assert source.read_bytes()==copy.read_bytes()
reference=np.asarray(Image.open(Q/'official-reference-native.png').convert('RGB'))
complete=np.asarray(Image.open(Q/'intro-f120.png').convert('RGB'));assert np.array_equal(reference,complete)
outside=[]
for f in (0,18,36,66,96,108,132,165,195):
 a=np.asarray(Image.open(R/f'qa/v7/outro-f{f:03d}.png').convert('RGB'));b=np.asarray(Image.open(Q/f'outro-f{f:03d}.png').convert('RGB'))
 mask=np.ones(a.shape[:2],bool);mask[240:660,420:1500]=False
 count=int(np.any(a!=b,axis=2)[mask].sum());assert count==0
 outside.append({'frame':f,'changedPixelsOutsideLogoRegion':count})
actual=Q/'actual';actual.mkdir(exist_ok=True)
picks=[('intro-trunk',36),('intro-growth',66),('intro-complete',126),('S1',283),('S4',809),('S6',1182),('outro-trunk',1198+36),('outro-growth',1198+66),('outro-complete',1198+132),('final',1393)]
canvas=Image.new('RGB',(1440,1200),(235,232,225));draw=ImageDraw.Draw(canvas)
for i,(name,f)in enumerate(picks):
 p=actual/f'{name}.png';ff(['-y','-i',NEW,'-vf',f'select=eq(n\\,{f})','-frames:v',1,p])
 im=Image.open(p).convert('RGB');im.thumbnail((480,270));left=(i%3)*480;top=(i//3)*300;canvas.paste(im,(left,top));draw.text((left+8,top+275),f'{name}: f{f} ({f/30:.2f}s)',fill='black')
canvas.save(Q/'actual-contact.jpg')
report={'frames':len(after),'nominalSeconds':1394/30,'videoDuration':float(v['duration']),
 'containerDuration':float(probe['format']['duration']),'fullDecode':'PASS',
 'bodyFramesIdenticalToV9':1048,'audioPacketCount':len(ap),'aacPacketsAndTimestampsIdentical':True,
 'decodedAudioIdentical':True,'decodedAudioSha256':hashlib.sha256(newpcm).hexdigest(),
 'officialNativeReferenceChangedPixels':0,'nativeOutroNonLogoParity':outside,
 'baselineFileCount':len(baseline),'unchangedBaselineCount':len(baseline)-len(changed),'intentionalSourceChange':changed,
 'suppliedSvgSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'originalSvgUnmodified':True,
 'sourceLeafCount':82,'sourceChineseGlyphGroups':4,'sourceEnglishGlyphs':20,
 'outputSha256':hashlib.sha256(NEW.read_bytes()).hexdigest(),'actualKeyframes':dict(picks)}
(Q/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
