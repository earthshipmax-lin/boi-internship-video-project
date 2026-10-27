from pathlib import Path
import subprocess,json,re,hashlib
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];q=R/'qa/closing-r01';movie=R/'out/BOI-HK_史詩形象片_v11_片尾修訂r01.mp4'
def run(cmd):return subprocess.run(cmd,check=True,capture_output=True,text=True)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
probe=json.loads(run(['ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_name,width,height,avg_frame_rate,nb_frames,sample_rate,channels','-of','json',str(movie)]).stdout)
run(['ffmpeg','-v','error','-i',str(movie),'-f','null','-'])
l=run(['ffmpeg','-hide_banner','-i',str(movie),'-af','loudnorm=I=-14.5:TP=-1.3:LRA=11:print_format=json','-f','null','-']).stderr
metrics=json.loads(re.findall(r'\{[\s\S]*?\}',l)[-1])
baseline=json.loads((q/'baseline.json').read_text());checks={p:digest(R.parent/p)==h for p,h in baseline.items()}
assert all(checks.values()),'Baseline changed'
assert probe['streams'][0]['nb_frames']=='2040'
assert 68<=float(probe['format']['duration'])<=68.03 # AAC packet tail padding
assert float(metrics['input_tp'])<=-1.0
for t in [59.2,60.4,61.8,62.1,63.8,66,67.9666667]:
 run(['ffmpeg','-v','error','-ss',str(t),'-i',str(movie),'-frames:v','1','-q:v','2',str(q/f'actual-{t:.2f}.jpg')])
panel=Image.new('RGB',(1440,870),'#182530');d=ImageDraw.Draw(panel)
for i,t in enumerate([59.2,60.4,61.8,62.1,63.8,66]):
 im=Image.open(q/f'actual-{t:.2f}.jpg').resize((720,405));x=(i%2)*720;y=(i//2)*290
 # 480x270 tiles make room for labels and a complete 2x3 contact sheet.
 im=im.resize((480,270));x=(i%3)*480;y=(i//3)*290;panel.paste(im,(x,y));d.text((x+10,y+272),f'{t:.2f}s',fill='white')
panel.crop((0,0,1440,580)).save(q/'actual-ending-contact.jpg')
native_a=np.asarray(Image.open(q/'still-66.00.png'));native_b=np.asarray(Image.open(q/'still-67.97.png'))
assert np.array_equal(native_a,native_b),'Native final hold differs'
reference=np.asarray(Image.open(R/'qa/v11/film/still-64_5.png'))
logo_native_equal=np.array_equal(reference[280:560,460:1460],native_b[280:560,460:1460])
assert logo_native_equal,'Final official lockup differs from v11 source rendering'
def audio(path):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-ac','1','-ar','48000','-f','f32le','-']),dtype='<f4')
encoded=audio(movie);ref=audio(R/'public/music/closing-r01/review-mix.wav');n=min(len(encoded),len(ref));corr=float(np.corrcoef(encoded[:n],ref[:n])[0,1])
assert corr>.999
old=audio(R/'out/BOI-HK_史詩形象片_v11.mp4');a=round(.3*48000);b=round(2.1*48000)
opening_db=float(20*np.log10(np.sqrt(np.mean(encoded[a:b]**2))/np.sqrt(np.mean(old[a:b]**2))))
report={'output':str(movie),'sha256':digest(movie),'probe':probe,'complete_decode_ok':True,'baseline_files_unchanged':len(checks),'baseline_checks':checks,'native_last_2s_frames_equal':True,'native_final_official_logo_region_equal_to_v11':bool(logo_native_equal),'audio_reference_correlation':corr,'final_loudness_lufs':float(metrics['input_i']),'final_true_peak_dbtp':float(metrics['input_tp']),'BGM_bus_change_db':-1.5,'measured_opening_music_only_vs_v11_db':opening_db,'new_voice_source_unmodified':digest(q/'ending-source.mp3')==digest(R/'public/vo/closing-r01/ending-source.mp3'),'review_limits':'No human listening verdict. Local tiny ASR misrecognizes Cantonese homophones; reference alignment is not proof of pronunciation. Drawl, excitement, music masking and edit seam need user playback.'}
(q/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['probe','baseline_checks']},ensure_ascii=False,indent=2))
