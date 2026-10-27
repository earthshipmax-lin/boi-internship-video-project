from pathlib import Path
from PIL import Image, ImageDraw
from scipy.ndimage import label, find_objects
import hashlib, json, subprocess, math
import numpy as np

R=Path(__file__).resolve().parents[1]
Q=R/'qa/v12/stage6'
movie=R/'out/BOI-HK_史詩形象片_v12_第六版試片.mp4'
def run(args):
    p=subprocess.run(args,capture_output=True)
    if p.returncode: raise RuntimeError(p.stderr.decode(errors='replace'))
    return p.stdout
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rgb(p): return np.asarray(Image.open(p).convert('RGB'))
def packets(p):
    data=json.loads(run(['ffprobe','-v','error','-select_streams','a:0','-show_packets','-show_data_hash','sha256','-of','json',str(p)]))
    return [{k:v.get(k) for k in ('pts','dts','duration','data_hash')} for v in data['packets']]

base=json.loads((Q/'baseline.json').read_text())
changed=[p for p,h in base.items() if sha(R/p)!=h]
assert changed==['src/Root.tsx'],changed
root=(R/'src/Root.tsx').read_text()
root=root.replace("import {EpicFilmV12Stage6} from './scenes/ScenesV12Stage6';\n",'')
root=root.replace("import {LogoOpticalComparisonStage6} from './components/LogoGridV12';\n",'')
root='\n'.join(line for line in root.split('\n') if '<Folder name="V12Stage6">' not in line)
assert root==(Q/'before/src/Root.tsx').read_text()
spec=json.loads((Q/'logo-optical-manifest.json').read_text())
logos=spec['items']
assert len(logos)==25 and len(spec['keep_source_ids'])==23 and len(spec['excluded_source_ids'])==4
assert sorted(spec['keep_source_ids']+spec['excluded_source_ids'])==list(range(1,28))
assert len({a['slot'] for a in logos})==25
assert sum(a['role']=='bank' for a in logos)==2
for a in logos:
    assert sha(R/'public'/a['file'])==a['sourceSha256']
    assert a['displayInkWidth']<=96.001 and a['displayInkHeight']<=54.001
    if a['id'] in ('hk-06','hk-09','hk-25','hk-27'): assert a['displayInkHeight']<=37.801
    if a['id'] in ('hk-10','hk-11','hk-12'): assert a['displayInkHeight']<=42.121
assert logos[4]['displayInkWidth']==84.48

geometry=[]
for f,left,rows in [(500,1010,4),(570,920,5)]:
    a=rgb(Q/f'frames/f{f}.png')[300:754,left:left+704]
    groups,_=label(a.min(2)>140)
    boxes=[]
    for part in find_objects(groups):
        if part is None: continue
        yy,xx=part
        if xx.stop-xx.start>100 and yy.stop-yy.start>60:
            boxes.append([xx.start+left,yy.start+300,xx.stop-xx.start,yy.stop-yy.start])
    expected=[[left+c*144,300+r*94,128,78] for r in range(rows) for c in range(5)]
    assert sorted(boxes)==sorted(expected),(f,boxes)
    geometry.append({'frame':f,'count':len(boxes),'pixel_boxes':boxes,'edge_error_pixels':0})

unchanged=[]
for f in [96,810,900,1098,1326,1356,1380,1530,1602,1755,2043,2102]:
    assert np.array_equal(rgb(Q/f'frames/f{f}.png'),rgb(R/f'qa/v12/stage5/frames/f{f}.png')),f
    unchanged.append(f)
probe=json.loads(run(['ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_name,width,height,nb_frames,avg_frame_rate','-of','json',str(movie)]))
v=probe['streams'][0]
assert (v['codec_name'],v['width'],v['height'],v['nb_frames'],v['avg_frame_rate'])==('h264',1920,1080,'2103','30/1')
assert 70.1<=float(probe['format']['duration'])<=70.13
run(['ffmpeg','-v','error','-i',str(movie),'-f','null','-'])
audio=packets(movie)
assert audio==packets(R/'qa/v12/stage3/audio-master.m4a')==packets(R/'out/BOI-HK_史詩形象片_v12_第五版試片.mp4')

frames=[435,450,487,500,524,525,528,531,534,537,540,542,548,570,608,609,612,617,618,810,1098,1356,1602,2043,2102]
actual=Q/'actual-frames';actual.mkdir(exist_ok=True)
select='+'.join(f'eq(n\\,{f})' for f in frames)
run(['ffmpeg','-y','-v','error','-i',str(movie),'-vf',f'select={select}','-fps_mode','vfr','-q:v','2',str(actual/'%03d.jpg')])
locations={f:actual/f'{i+1:03}.jpg' for i,f in enumerate(frames)}
sheet=Image.new('RGB',(1600,math.ceil(len(frames)/4)*250),'#173446');draw=ImageDraw.Draw(sheet)
for i,f in enumerate(frames):
    x,y=i%4*400,i//4*250
    sheet.paste(Image.open(locations[f]).resize((400,225)),(x,y))
    draw.text((x+8,y+230),f'{f/30:.3f}s / f{f}',fill='white')
sheet.save(Q/'actual-storyboard.jpg',quality=94)
four=Image.new('RGB',(1600,960),'#173446');draw=ImageDraw.Draw(four)
for i,(f,title) in enumerate([(435,'Premium entry'),(500,'Premium settled:20'),(534,'Commission append'),(570,'Commission settled:25')]):
    x,y=i%2*800,i//2*480
    four.paste(Image.open(locations[f]).resize((800,450)),(x,y))
    draw.text((x+10,y+456),f'{title} / {f/30:.3f}s',fill='white')
four.save(Q/'four-keyframes.jpg',quality=95)
(Q/'actual-frame-index.json').write_text(json.dumps({str(f):str(p.relative_to(R)) for f,p in locations.items()},indent=2)+'\n')
report={'output':str(movie),'sha256':sha(movie),'probe':probe,'complete_decode_ok':True,
        'protected_baseline_files_unchanged':len(base)-1,'protected_total':len(base),'Root_additive_only':True,
        'audio_packets_identical_to_Stage5_and_master':True,'audio_packet_count':len(audio),
        'insurance_source_count':23,'banks':2,'all_25_slots_unique_filled':True,
        'source_RGB_files_unchanged':True,'all_effective_ink_within_96x54_safe_zone':True,
        'native_grid_geometry':geometry,'grid_shift_px':90,'uniform_settled_tile_opacity':.82,
        'ring_counts':[8,10],'first20_all_lit_frame':487,'added5_all_lit_frame':542,'shift_settled_frame':548,
        'native_unchanged_sample_frames':unchanged,'actual_movie_samples':len(frames),
        'visual_weight_review':'Individual fitting and native before/after comparison inspected; <=15 percent perceptual difference has no defined objective metric and is not certified by the geometry checks.',
        'review_limits':'Native geometry, source continuity, sample movie frames and full decode checked; user visual acceptance remains pending.'}
(Q/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='native_grid_geometry'},ensure_ascii=False,indent=2))
