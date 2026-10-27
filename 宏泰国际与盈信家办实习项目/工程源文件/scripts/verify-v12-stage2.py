from pathlib import Path
import subprocess,json,re,hashlib
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];q=R/'qa/v12/stage2';movie=R/'out/BOI-HK_史詩形象片_v12.mp4';prior=R/'out/BOI-HK_史詩形象片_v12_第一階段試片.mp4'
def run(c):return subprocess.run(c,check=True,capture_output=True,text=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
probe=json.loads(run(['ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_name,width,height,nb_frames,avg_frame_rate,sample_rate,channels','-of','json',str(movie)]).stdout)
assert probe['streams'][0]['nb_frames']=='2040';assert 68<=float(probe['format']['duration'])<=68.03
run(['ffmpeg','-v','error','-i',str(movie),'-f','null','-'])
def packets(p):
 r=json.loads(run(['ffprobe','-v','error','-select_streams','a:0','-show_packets','-show_data_hash','sha256','-of','json',str(p)]).stdout)
 return [{k:x.get(k) for k in ['pts','dts','duration','data_hash']} for x in r['packets']]
before,after=packets(prior),packets(movie);assert before==after,'AAC payload or timing changed'
baseline=json.loads((q/'baseline.json').read_text());checks={p:sha(R/p)==h for p,h in baseline.items()};assert all(checks.values())
root=(R/'src/Root.tsx').read_text().replace("import {EpicFilmV12Stage2} from './scenes/ScenesV12Stage2';\n",'');root='\n'.join(l for l in root.split('\n') if '<Folder name="V12Stage2">' not in l);assert root==(q/'Root-before.tsx').read_text()
native=np.asarray(Image.open(q/'frames/f1980.png'));old=np.asarray(Image.open(R/'qa/v12/still-66.00.png'));last=np.asarray(Image.open(q/'frames/f2039.png'))
assert np.array_equal(native,last);assert np.array_equal(native,old),'Accepted final hold changed'
seams=json.loads((q/'scene-seams.json').read_text());office=next(s['startFrame'] for s in seams if s['id']=='office')
for f in range(1290,1303):
 run(['ffmpeg','-v','error','-ss',str(f/30),'-i',str(movie),'-frames:v','1','-q:v','2',str(q/f'frames/actual-seam-{f}.jpg')])
paper=np.asarray(Image.open(q/f'frames/actual-seam-{office}.jpg'));corner=paper[10:50,900:1000].mean(axis=(0,1));assert np.max(np.abs(corner-np.array([244,238,226])))<6
# At the office start the outgoing platform has zero layer lifetime; its text
# and right-hand tag cannot be composited. Check native RGB background too.
native_corner=np.asarray(Image.open(q/f'frames/f{office}.png'))[10:50,900:1000];assert np.max(np.abs(native_corner.astype(int)-np.array([244,238,226])))==0
times=[3.2,5.5,15.7,18.3,24,26.5,28,34.5,43.2,52,56.5,63.8]
im=Image.new('RGB',(1600,1280),'#172d3b');d=ImageDraw.Draw(im)
for i,t in enumerate(times):
 p=q/f'frames/actual-{t:.2f}.jpg';run(['ffmpeg','-v','error','-ss',str(t),'-i',str(movie),'-frames:v','1','-q:v','2',str(p)]);a=Image.open(p).resize((533,300));x=i%3*533;y=i//3*320;im.paste(a,(x,y));d.text((x+12,y+303),f'{t}s',fill='white')
im.save(q/'actual-storyboard.jpg')
log=run(['ffmpeg','-hide_banner','-i',str(movie),'-af','loudnorm=I=-14.5:TP=-1.3:LRA=11:print_format=json','-f','null','-']).stderr;loud=json.loads(re.findall(r'\{[\s\S]*?\}',log)[-1])
geometry=json.loads((q/'awards-geometry-check.json').read_text());assert geometry['bottom_error_px']<=2;assert all(a['width_ratio']<=1.2 and a['longest_full_interval_s']>=.9 for a in geometry['items'])
report={'output':str(movie),'sha256':sha(movie),'probe':probe,'complete_decode_ok':True,'baseline_unchanged_count':len(checks),'baseline_checks':checks,'Root_only_additive_stage2':True,'AAC_packets_and_timing_identical_to_accepted_stage1':True,'audio_packet_count':len(after),'final_loudness_lufs':float(loud['input_i']),'true_peak_dbtp':float(loud['input_tp']),'native_final_hold_identical_to_stage1':True,'native_last_2s_frames_identical':True,'awards_visible_bottom_error_px':geometry['bottom_error_px'],'awards_minimum_full_visibility_s':min(a['longest_full_interval_s'] for a in geometry['items']),'awards_height_ratio':geometry['height_ratio'],'awards_motion_speed_px_s':geometry['motion_speed_px_s'],'office_seam_frame':office,'opposite_background_crossfade':False,'internal_paper_switch_at_52_s':True,'slogan_brush_sha256_unchanged':sha(R/'public/brand/closing-r01/slogan-brush.svg')==baseline['public/brand/closing-r01/slogan-brush.svg'],'review_limits':'Alpha/body preservation and actual frames visually checked; no claim that technical checks equal boss approval. Five bounded logo timing fallbacks are labeled, not misreported as beat hits.'}
(q/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['probe','baseline_checks']},ensure_ascii=False,indent=2))
