"""Verify the user's all-logos-before-cut acceptance condition and audio continuity."""
from pathlib import Path
import hashlib,json,subprocess
import numpy as np
from PIL import Image,ImageDraw

R=Path(__file__).resolve().parents[1]
Q=R/'qa/v12/stage2-logo-r01'
MOVIE=R/'out/BOI-HK_史詩形象片_v12_Logo加速修訂.mp4'
PRIOR=R/'out/BOI-HK_史詩形象片_v12.mp4'

def run(args):
    return subprocess.run(args,check=True,capture_output=True,text=True)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def packets(path):
    data=json.loads(run(['ffprobe','-v','error','-select_streams','a:0','-show_packets','-show_data_hash','sha256','-of','json',str(path)]).stdout)
    return [{k:p.get(k) for k in ('pts','dts','duration','data_hash')} for p in data['packets']]

probe=json.loads(run(['ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_name,width,height,nb_frames,avg_frame_rate','-of','json',str(MOVIE)]).stdout)
assert probe['streams'][0]['nb_frames']=='2040'
assert probe['streams'][0]['width']==1920 and probe['streams'][0]['height']==1080
assert probe['streams'][0]['avg_frame_rate']=='30/1'
assert 68<=float(probe['format']['duration'])<=68.03
run(['ffmpeg','-v','error','-i',str(MOVIE),'-f','null','-'])
old_audio,new_audio=packets(PRIOR),packets(MOVIE)
assert old_audio==new_audio,'AAC payload or timing changed'

base=json.loads((Q/'baseline.json').read_text())
checks={p:sha(R/p)==h for p,h in base.items()}
changed=[p for p,ok in checks.items() if not ok]
assert changed==['src/config/logos-stage2.json'],changed
spec=json.loads((R/'src/config/logos-stage2.json').read_text())
previous=json.loads((Q/'before/src/config/logos-stage2.json').read_text())
assert spec['keep_ids']==previous['keep_ids'] and len(spec['keep_ids'])==25
rev=spec['lighting_revision'];full=rev['all_lit_frame'];cut=rev['next_scene_frame']
premium=next(s for s in json.loads((Q/'scene-seams.json').read_text()) if s['id']=='premium')
assert premium['startFrame']==rev['scene_start_frame'] and premium['endFrame']==cut
assert (Q/'scene-seams.json').read_bytes()==(R/'qa/v12/stage2/scene-seams.json').read_bytes()
for frame in range(full,cut+1):
    for slot in spec['light_schedule']:
        p=max(0,min(1,(frame/30-slot['time'])/rev['fade_seconds']))
        assert .14+.86*(1-(1-p)**4)==1
assert cut-full>=24,'All-lit hold must be at least 0.8 seconds'

# Inspect the exported H264 rather than relying on the schedule alone.
frames=[432,441,459,477,489,500,510,524,525,534,549,600]
select='+'.join(f'eq(n\\,{f})' for f in frames)
run(['ffmpeg','-y','-v','error','-i',str(MOVIE),'-vf',f'select={select}','-fps_mode','vfr','-q:v','2',str(Q/'frames/actual-%02d.jpg')])
levels={}
for frame in (500,510,524,525):
    img=np.asarray(Image.open(Q/f'frames/actual-{frames.index(frame)+1:02}.jpg').convert('RGB'))
    values=[]
    for i in range(25):
        x=1040+(i%5)*153;y=280+(i//5)*92
        values.append(round(float(np.quantile(img[y:y+80,x:x+142].min(axis=2),.85)),2))
    assert min(values)>=245,{'frame':frame,'white_levels':values}
    levels[str(frame)]=values

native_checks={}
for f in (720,1035,1291,1560,1980,2039):
    native_checks[str(f)]=np.array_equal(np.asarray(Image.open(Q/f'frames/f{f}.png')),np.asarray(Image.open(R/f'qa/v12/stage2/frames/f{f}.png')))
assert all(native_checks.values()),native_checks
sheet=Image.new('RGB',(1280,6*385),'#142d3d');d=ImageDraw.Draw(sheet)
for i,f in enumerate(frames):
    img=Image.open(Q/f'frames/actual-{i+1:02}.jpg').resize((640,360));x=i%2*640;y=i//2*385
    sheet.paste(img,(x,y));d.text((x+10,y+364),f'{f/30:.3f}s / frame {f}',fill='white')
sheet.save(Q/'actual-logo-sequence.jpg',quality=91)

report={'output':str(MOVIE),'sha256':sha(MOVIE),'probe':probe,'complete_decode_ok':True,'all_25_fully_lit_frame':full,'all_lit_seconds':full/30,'next_scene_frame':cut,'next_scene_seconds':cut/30,'full_brightness_hold_seconds':(cut-full)/30,'all_lit_on_every_frame_until_cut':True,'actual_H264_grid_white_level_min':min(min(v) for v in levels.values()),'actual_H264_grid_white_levels':levels,'AAC_packets_and_timing_identical_to_previous':True,'audio_packet_count':len(new_audio),'baseline_unchanged_count':sum(checks.values()),'baseline_changed_files':changed,'native_unaffected_frame_checks':native_checks,'all_scene_times_unchanged':True,'commission_group_opacity_preserved':spec['commission_opacity'],'review_limit':'Technical acceptance checked; user review of the updated pace remains separate.'}
(Q/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('probe','actual_H264_grid_white_levels')},ensure_ascii=False,indent=2))
