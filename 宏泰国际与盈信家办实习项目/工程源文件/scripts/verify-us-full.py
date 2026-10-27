from pathlib import Path
import json,subprocess,hashlib,re,numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];q=R/'qa/us-v1-60s';p=R/'out/US-Team-v1_60s_初版.mp4';T=json.loads((q/'timeline.json').read_text())
subprocess.run(['ffmpeg','-v','error','-i',str(p),'-f','null','-'],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]));v=next(s for s in probe['streams'] if s['codec_type']=='video');assert v['width']==1920 and v['height']==1080 and v['nb_frames']=='1800' and float(probe['format']['duration'])==60
A=json.loads((q/'frame-audit.json').read_text());assert len(A)==1800 and all(a['scene'] and a['playbackRate']==1 for a in A.values())
base=json.loads((q/'baseline.json').read_text());changed=[x for x,h in base.items() if hashlib.sha256((R.parent/x).read_bytes()).hexdigest()!=h];assert set(changed)=={'video/src/Root.tsx','video/src/config/performance-us-v1.json'},changed
root=(R/'src/Root.tsx').read_text().replace("import {USFilm60V1} from './scenes/USFilm60V1';\n",'').replace('<Composition id="US-Team-v1-60s" component={USFilm60V1} width={1920} height={1080} fps={30} durationInFrames={1800} defaultProps={{qa:false}}/>','');assert root==(q/'source/Root-before.tsx').read_text()
x=np.array(Image.open(q/'frames/team-full-f120.png'));y=np.array(Image.open(q/'frames/team-reference-f120.png'));assert np.array_equal(x[:1000],y[:1000]);assert not np.array_equal(x[1000:],y[1000:])
assert (R/'public/vo/us-v1/full/S2.wav').read_bytes()==(R/'public/vo/us-v1/team-b/VO-01.wav').read_bytes()
source=(R/'src/scenes/USFilm60V1.tsx').read_text();assert not re.search('[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]',source);assert source.count('Internal review — not for distribution')==1
people=json.loads((R/'src/config/us-team-v1.json').read_text());assert len(people)==6 and max(r['scale'] for r in people)<=1
for s in T['scenes']:assert s['voiceStartFrame']/30+s['duration']<=s['endFrame']/30
# Final AAC compared with the complete stereo master, rather than an unrelated voice test.
def pcm(f):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(f),'-ar','48000','-ac','2','-f','f32le','-']),np.float32)
a,b=pcm(p),pcm(R/'public/music/us-v1/full-review-mix.wav');n=min(len(a),len(b));corr=float(np.corrcoef(a[:n],b[:n])[0,1]);assert corr>.999
log=subprocess.run(['ffmpeg','-hide_banner','-i',str(p),'-vn','-af','loudnorm=I=-16:TP=-1:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True).stderr;l=json.JSONDecoder().raw_decode(log[log.rindex('{'):])[0];assert float(l['input_tp'])<=-1
sheet=Image.new('RGB',(1280,1600),'#e9e5df');d=ImageDraw.Draw(sheet);font=ImageFont.truetype(str(R/'public/fonts/Geist.ttf'),20)
for i,s in enumerate(T['scenes']):
 frame=s['startFrame']+min(s['endFrame']-s['startFrame']-20,240 if i==6 else round((s['endFrame']-s['startFrame'])*.7));f=q/f'frames/actual-S{i}.png';subprocess.run(['ffmpeg','-v','error','-y','-i',str(p),'-vf',f'select=eq(n\\,{frame})','-frames:v','1',str(f)],check=True);im=Image.open(f);im.thumbnail((624,351));cx=i%2*640;cy=i//2*400;sheet.paste(im,(cx,cy+32));d.text((cx+12,cy+4),f"S{i} / {frame/30:.2f}s",fill='#24211f',font=font)
sheet.save(q/'actual-storyboard.jpg')
r={'status':'technical_checks_passed_user_playback_pending','duration':60,'frames':1800,'fps':30,'width':1920,'height':1080,'fullDecodePassed':True,'auditedFrames':len(A),'englishTextSourceCheck':True,'teamNativeFrameIdenticalExceptRemovedFooter':True,'S2AudioByteIdentical':True,'allPortraitScalesAtMost1':True,'protectedFiles':len(base),'unchangedProtectedFiles':len(base)-2,'changedFiles':changed,'rootOnlyAdditive':True,'allHKAndPriorUSPilotsUnchanged':True,'finalAudioMasterCorrelation':corr,'loudnessLUFS':l['input_i'],'truePeakDBTP':l['input_tp'],'musicSource':'original additive keyboard composition, no external samples','releaseStatus':'internal_review_only','sha256':hashlib.sha256(p.read_bytes()).hexdigest()};(q/'verification.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
