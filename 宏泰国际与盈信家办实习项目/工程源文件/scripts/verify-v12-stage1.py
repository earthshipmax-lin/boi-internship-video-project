from pathlib import Path
import subprocess,json,re,hashlib
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];q=R/'qa/v12';movie=R/'out/BOI-HK_史詩形象片_v12_第一階段試片.mp4'
def run(c):return subprocess.run(c,check=True,capture_output=True,text=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
probe=json.loads(run(['ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_name,width,height,nb_frames,avg_frame_rate,sample_rate,channels','-of','json',str(movie)]).stdout)
assert probe['streams'][0]['nb_frames']=='2040'
assert probe['streams'][0]['width']==1920 and probe['streams'][0]['height']==1080
assert 68<=float(probe['format']['duration'])<=68.03
run(['ffmpeg','-v','error','-i',str(movie),'-f','null','-'])
log=run(['ffmpeg','-hide_banner','-i',str(movie),'-af','loudnorm=I=-14.5:TP=-1.3:LRA=11:print_format=json','-f','null','-']).stderr
loud=json.loads(re.findall(r'\{[\s\S]*?\}',log)[-1]);assert float(loud['input_tp'])<=-1.0
baseline=json.loads((q/'baseline.json').read_text());checks={p:sha(R/p)==h for p,h in baseline.items()};assert all(checks.values())
root=(R/'src/Root.tsx').read_text().replace("import {EpicFilmV12} from './scenes/ScenesV12';\n",'');root='\n'.join(l for l in root.split('\n') if '<Folder name="V12">' not in l);assert root==(q/'Root-before.tsx').read_text()
times=[3.5,15.7,18.9,24.2,26.5,28,31.26,31.6,32.2,32.4,32.9,33.46,33.8,34.5,40.5,63.5,66,67.9666667]
for t in times:run(['ffmpeg','-v','error','-ss',str(t),'-i',str(movie),'-frames:v','1','-q:v','2',str(q/f'actual-{t:.2f}.jpg')])
im=Image.new('RGB',(1600,1280),'#152e3e');d=ImageDraw.Draw(im)
for i,t in enumerate([3.5,15.7,18.9,24.2,26.5,28,31.6,32.2,32.9,33.8,34.5,63.5]):
 a=Image.open(q/f'actual-{t:.2f}.jpg').resize((533,300));x=i%3*533;y=i//3*320;im.paste(a,(x,y));d.text((x+12,y+303),f'{t}s',fill='white')
im.save(q/'actual-storyboard.jpg')
native1=np.asarray(Image.open(q/'still-66.00.png'));native2=np.asarray(Image.open(q/'still-67.97.png'));assert np.array_equal(native1,native2)
def audio(p):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-ac','1','-ar','48000','-f','f32le','-']),dtype='<f4')
a=audio(movie);b=audio(R/'public/music/v12/review-mix.wav');n=min(len(a),len(b));corr=float(np.corrcoef(a[:n],b[:n])[0,1]);assert corr>.999
report={'output':str(movie),'sha256':sha(movie),'probe':probe,'complete_decode_ok':True,'baseline_unchanged_count':len(checks),'baseline_checks':checks,'Root_only_additive_v12':True,'last_2s_native_frames_identical':True,'final_loudness_lufs':float(loud['input_i']),'true_peak_dbtp':float(loud['input_tp']),'audio_reference_correlation':corr,'voice_source_hash_preserved':sha(q/'ending-source-r02.mp3')==sha(R/'public/vo/hk-v12/ending-source-r02.mp3'),'photo_stage':'P1 27 HK provider logos + 2 bank logos; P2 8 award crops. City-photo expansion remains next gate.','route_checks':'route-check.json; first active frame within 1 frame of reference cue, not human-certified word timing','review_limits':'No human verdict on increased excitement, natural tails, masking or beat feel; source-code geometry, rendered keyframes and technical data are distinct.'}
(q/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['probe','baseline_checks']},ensure_ascii=False,indent=2))
