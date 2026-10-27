from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json,subprocess,re
R=Path(__file__).resolve().parents[1];q=R/'qa/us-v1'
base=json.loads((q/'protected-baseline.json').read_text());changed=[p for p,h in base.items() if hashlib.sha256((R.parent/p).read_bytes()).hexdigest()!=h];assert changed==['video/src/Root.tsx'],changed
old=(q/'source/Root-before.tsx').read_text();new=(R/'src/Root.tsx').read_text();rest=new.replace("import {USTeamV1} from './scenes/USTeamV1';\n",'').replace('\n <Folder name="US"><Composition id="US-Team-v1" component={USTeamV1} width={1920} height={1080} fps={30} durationInFrames={240} defaultProps={{qa:false}}/></Folder>','');assert rest==old
rec=json.loads((q/'portraits.json').read_text());assert len(rec)==6 and len(set(r['sourceSha256'] for r in rec))==6
assert all(r['scale']<=1 for r in rec)
audit=json.loads((q/'frame-audit.json').read_text());assert len(audit)==240
for frame,a in audit.items():
 assert a['count']==6
 for i,p in enumerate(a['people']):
  assert p['w']==224 and p['h']==280 and p['x']%8==0 and p['y']%8==0 and p['scale']<=1
  assert p['enterFrame']==i*3 and p['nameFrame']==i*3+6
  assert p['y']+280+80<=984
source=(R/'src/scenes/USTeamV1.tsx').read_text();assert not re.search('[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]',source)
film=R/'out/US-Team-v1-visual-study.mp4'
subprocess.run(['ffmpeg','-v','error','-i',str(film),'-f','null','-'],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(film)]));v=probe['streams'][0];assert v['width']==1920 and v['height']==1080 and v['nb_frames']=='240' and probe['format']['duration']=='8.000000'
actual=q/'actual-f120.png';subprocess.run(['ffmpeg','-v','error','-y','-i',str(film),'-vf','select=eq(n\\,120)','-frames:v','1',str(actual)],check=True)
im=Image.open(actual);contact=Image.new('RGB',(752,640),'#e9e5df');d=ImageDraw.Draw(contact);font=ImageFont.truetype(str(R/'public/fonts/Geist.ttf'),15)
for i,p in enumerate(audit['120']['people']):
 x,y=p['x'],p['y'];crop=im.crop((x,y,x+224,y+280));crop.save(q/f"actual-100pct-{rec[i]['slug']}.png");cx=(i%3)*264;cy=(i//3)*320;contact.paste(crop,(cx,cy+24));d.text((cx,cy+2),p['name'],font=font,fill='#24211f')
contact.save(q/'actual-faces-100pct.png')
scale=Image.new('RGB',(960,336),'#e9e5df');d=ImageDraw.Draw(scale)
for i,r in enumerate(rec):d.text((24,24+i*44),f"{r['name']:<18}  {r['nativeSize'][0]}x{r['nativeSize'][1]} -> 224x280   scale {r['scale']:.6f} <= 1",font=font,fill='#24211f')
scale.save(q/'scale-calculation.png')
result={'status':'technical_visual_checks_passed_user_review_pending','composition':'US-Team-v1','duration':8,'frames':240,'fps':30,'portraitCount':6,'maxScale':max(r['scale'] for r in rec),'all240FramesAudited':True,'protectedFileCount':len(base),'unchangedProtectedFiles':len(base)-1,'rootOnlyAdditive':True,'hkV12FilesUnchanged':True,'audio':'none - final voice pending user selection','wordAlignmentAccuracy':'not certified; requested 0.35 ms below practical Whisper resolution','sha256':hashlib.sha256(film.read_bytes()).hexdigest()}
(q/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
