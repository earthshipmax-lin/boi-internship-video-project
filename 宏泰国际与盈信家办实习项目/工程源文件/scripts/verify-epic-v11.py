from pathlib import Path
import subprocess,json,re,hashlib,math
from PIL import Image,ImageDraw
import numpy as np
ROOT=Path(__file__).resolve().parents[1];q=ROOT/'qa/v11/film';p=ROOT/'out/BOI-HK_史詩形象片_v11.mp4'
def run(cmd):return subprocess.check_output(cmd)
probe=json.loads(run(['ffprobe','-v','error','-show_entries','format=duration,size:stream=index,codec_name,width,height,avg_frame_rate,nb_frames,sample_rate,channels','-of','json',str(p)]))
v=next(s for s in probe['streams'] if s['codec_name']=='h264');assert v['width']==1920 and v['height']==1080 and v['nb_frames']=='2040'
assert abs(float(probe['format']['duration'])-68)<.05
r=subprocess.run(['ffmpeg','-v','error','-i',str(p),'-f','null','-'],capture_output=True,text=True);assert r.returncode==0,r.stderr
last=run(['ffmpeg','-v','error','-sseof','-2','-i',str(p),'-an','-f','framemd5','-']).decode();hashes=[s.split(',')[-1].strip() for s in last.splitlines() if not s.startswith('#') and ',' in s];assert len(hashes)>=59
# H264 I/P quantization can vary on a completely static source: verify source identity, then bound decoded differences.
source_a=np.array(Image.open(q/'still-66.png').convert('RGB'));source_b=np.array(Image.open(q/'still-67_96666666666667.png').convert('RGB'));assert np.array_equal(source_a,source_b),'Source hold is moving'
raw=run(['ffmpeg','-v','error','-sseof','-2','-i',str(p),'-vf',"select='eq(n,0)+eq(n,59)'",'-fps_mode','vfr','-an','-f','rawvideo','-pix_fmt','rgb24','-']);two=np.frombuffer(raw,np.uint8).reshape(-1,1080,1920,3);lossy_delta=float(np.abs(two[-1].astype(np.int16)-two[0].astype(np.int16)).mean());assert lossy_delta<1.0,('Unexpected decoded hold change',lossy_delta)
loud=subprocess.run(['ffmpeg','-hide_banner','-i',str(p),'-vn','-af','loudnorm=I=-14:TP=-1:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True).stderr
lm=json.loads(re.findall(r'\{[\s\S]*?\}',loud)[-1]);(q/'final-loudness.json').write_text(json.dumps(lm,indent=2)+'\n')
if float(lm['input_tp'])>-1.0:print('TRUE PEAK ABOVE TARGET:',lm['input_tp'],flush=True)
times=[3.5,9,15.7,18.9,21.7,25.5,32.5,40.5,45.5,50.5,56.5,64.5,67.5]
im=Image.new('RGB',(1600,1000),'#071D2A');draw=ImageDraw.Draw(im)
for i,t in enumerate(times):
 out=q/f'actual-{str(t).replace(".","_")}.jpg'
 subprocess.run(['ffmpeg','-v','error','-ss',str(t),'-i',str(p),'-frames:v','1','-q:v','2','-y',str(out)],check=True)
 picture=Image.open(out).convert('RGB');picture.thumbnail((400,225));x=(i%4)*400;y=(i//4)*250;im.paste(picture,(x,y));draw.text((x+12,y+230),f'{t}s',fill='white')
im.save(q/'actual-storyboard.jpg',quality=94)
# Check selected source fidelity and manifest isolation.
selection=json.loads((ROOT/'qa/v11/CURRENT_SELECTION.json').read_text());assert hashlib.sha256((ROOT/'public/music/v11/bgm-A.mp3').read_bytes()).hexdigest()==selection['selected_music']['sha256']
voice=json.loads((ROOT/'qa/v11/voice-r06/verification.json').read_text());assert hashlib.sha256((ROOT/'public/vo/hk-v11/full-r06.mp3').read_bytes()).hexdigest()==voice['sha256']
assert not (ROOT/'public/music/v11/bgm-B.mp3').exists() and not (ROOT/'public/music/v11/bgm-C.mp3').exists()
oldroot=(ROOT/'src/Root.tsx').read_text().replace("import {EpicFilmV11} from './scenes/ScenesV11';\n",'').replace(' <Folder name="V11"><Composition id="BOI-HK-Epic-v11" component={EpicFilmV11} width={1920} height={1080} fps={30} durationInFrames={2040}/></Folder>\n','')
(q/'Root-before-v11-reconstructed.tsx').write_text(oldroot)
report={'output':str(p),'probe':probe,'complete_decode_ok':True,'last_2s_frames':len(hashes),'last_2s_unique_frame_hashes':len(set(hashes)),'last_hold_native_frames_equal':True,'decoded_hold_first_last_mean_abs_rgb':lossy_delta,'hold_note':'Native source frames at66.0 and67.9667 are identical; decoded H264 can differ slightly from temporal quantization.','loudness_lufs':float(lm['input_i']),'true_peak_dbtp':float(lm['input_tp']),'voice_source_hash_unchanged':True,'music_A_hash_unchanged':True,'BC_excluded_from_active_music':True,'caption_method':'Reference-text forced alignment; not independent Cantonese transcription','subjective_review':'Not performed by a human; user must judge epic scale, voice feeling, music seams and masking.','status':'internal review sample, not externally approved'}
(q/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
