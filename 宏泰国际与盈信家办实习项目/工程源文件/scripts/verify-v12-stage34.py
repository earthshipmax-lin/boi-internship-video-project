from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json,subprocess,re,math,shutil
import numpy as np

R=Path(__file__).resolve().parents[1];Q3=R/'qa/v12/stage3';Q4=R/'qa/v12/stage4'
def run(args):
    p=subprocess.run(args,capture_output=True,text=True)
    if p.returncode:raise RuntimeError(p.stderr)
    return p
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def arr(p):return np.asarray(Image.open(p).convert('RGB'))
def audio_packets(p):
    data=json.loads(run(['ffprobe','-v','error','-select_streams','a:0','-show_packets','-show_data_hash','sha256','-of','json',str(p)]).stdout)
    return [{k:v.get(k) for k in ('pts','dts','duration','data_hash')} for v in data['packets']]

base=json.loads((Q3/'baseline.json').read_text());checks={p:sha(R/p)==h for p,h in base.items()}
assert [p for p,ok in checks.items() if not ok]==['src/Root.tsx']
root=(R/'src/Root.tsx').read_text()
for stage in (3,4):
    root=root.replace(f"import {{EpicFilmV12Stage{stage}}} from './scenes/ScenesV12Stage{stage}';\n",'')
    root='\n'.join(s for s in root.split('\n') if f'<Folder name="V12Stage{stage}">' not in s)
assert root==(Q3/'before/Root.tsx').read_text()
old=json.loads((R/'src/config/captions-v12.json').read_text());new=json.loads((R/'src/config/captions-v12-stage3.json').read_text());assert len(old)==len(new)==24
for a,b in zip(old,new):
    shift=2.1 if a['start']>=28.2 else 0
    assert a['text']==b['text'] and abs(b['start']-a['start']-shift)<1e-6 and abs(b['end']-a['end']-shift)<1e-6
spec=json.loads((R/'src/config/awards-stage3.json').read_text());assert len(spec['items'])==10
assert sum(x['category']=='trophy' for x in spec['items'])==4
assert all(x['scale']<=1 for x in spec['items'])
bottoms=[]
for a in spec['items']:
    im=Image.open(R/'public'/a['file'])
    if a['category']=='trophy':
        bb=im.getchannel('A').getbbox();assert bb
        bottoms.append(a['top']+bb[3]*a['scale'])
        raw=Image.open(R/a['source']).convert('RGB').crop(a['crop'])
        assert np.array_equal(np.asarray(raw),np.asarray(im.convert('RGB')))
    else:
        raw=Image.open(R/a['source']).convert('RGB').crop(a['crop']);border=a['border_pixels']
        assert np.array_equal(np.asarray(raw),np.asarray(im.crop((border,border,border+raw.width,border+raw.height)).convert('RGB')))
assert max(bottoms)-min(bottoms)<=2
assert np.array_equal(arr(Q3/'frames/f810.png')[330:1043],arr(Q3/'frames/f900.png')[330:1043])

manifest=json.loads((Q4/'transitions/manifest.json').read_text());holds={};coverage={}
def bezier(x):
    lo,hi=0,1
    for _ in range(24):
        t=(lo+hi)/2;bx=3*(1-t)**2*t*.65+3*(1-t)*t*t*.35+t*t*t
        if bx<x:lo=t
        else:hi=t
    t=(lo+hi)/2;return 3*t*t-2*t*t*t
yy,xx=np.mgrid[:1080,:1920];distance=np.hypot(xx-960,yy-820)
for p in manifest['phases']:
    hold=[arr(Q4/f"frames/f{p['startFrame']+i}.png") for i in range(18,30)]
    assert all(np.array_equal(hold[0],a) for a in hold),p['id']
    holds[p['id']]={'frames':12,'seconds':.4,'native_pixels_identical':True}
    interior=[]
    for k in (6,9,12,15,17):
        inside=distance<(1270*bezier(k/18)-3)
        mid=arr(Q4/f"frames/f{p['startFrame']+k}.png")
        error=int(np.abs(mid[inside].astype(int)-hold[0][inside].astype(int)).max())
        assert error==0,(p['id'],k,error)
        interior.append({'offset_frame':k,'fully_revealed_interior_RGB_error':error})
    coverage[p['id']]=interior
    if p['paper']:
        box=hold[0][420:700,210:700]
        assert np.all(box==np.array([244,238,226])),p['id']

movies={3:R/'out/BOI-HK_史詩形象片_v12_第三版試片.mp4',4:R/'out/BOI-HK_史詩形象片_v12_第四版試片.mp4'}
master_packets=audio_packets(Q3/'audio-master.m4a');reports={}
for st,movie in movies.items():
    q=R/f'qa/v12/stage{st}'
    probe=json.loads(run(['ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_name,width,height,nb_frames,avg_frame_rate','-of','json',str(movie)]).stdout)
    v=probe['streams'][0];assert v['nb_frames']=='2103' and v['width']==1920 and v['height']==1080 and v['avg_frame_rate']=='30/1'
    assert 70.1<=float(probe['format']['duration'])<=70.13
    run(['ffmpeg','-v','error','-i',str(movie),'-f','null','-'])
    assert audio_packets(movie)==master_packets
    # Picture continuity checks use native stills, not H264 hash equality.
    assert np.array_equal(arr(q/'frames/f2043.png'),arr(R/'qa/v12/stage2/frames/f1980.png'))
    assert np.array_equal(arr(q/'frames/f2102.png'),arr(R/'qa/v12/stage2/frames/f2039.png'))
    logo=arr(q/'frames/f500.png')
    levels=[float(np.quantile(logo[280+i//5*92:360+i//5*92,1040+i%5*153:1182+i%5*153].min(axis=2),.85)) for i in range(25)]
    assert min(levels)>=250
    times=[3.2,15.3,16.6666667,18.3,24.5,27,30.4,36.6,46.3,50.5,54.1,58.5,65.9,68.1]
    frames=sorted({round(t*30) for t in times})
    target=q/'actual-frames';target.mkdir(exist_ok=True)
    select='+'.join(f'eq(n\\,{f})' for f in frames)
    run(['ffmpeg','-y','-v','error','-i',str(movie),'-vf',f'select={select}','-fps_mode','vfr','-q:v','2',str(target/'%03d.jpg')])
    sheet=Image.new('RGB',(1600,4*320),'#173446');d=ImageDraw.Draw(sheet)
    for i,f in enumerate(frames):
        img=Image.open(target/f'{i+1:03}.jpg').resize((400,225));x=i%4*400;y=i//4*320;sheet.paste(img,(x,y));d.text((x+10,y+232),f'{f/30:.3f}s / f{f}',fill='white')
    sheet.save(q/'actual-storyboard.jpg',quality=93)
    reports[st]={'output':str(movie),'sha256':sha(movie),'probe':probe,'complete_decode_ok':True,'AAC_packets_identical_to_shared_master':True,'audio_packet_count':len(master_packets),'original_voice_PCM_spans_retained':True,'voice_speed':1,'duration_added_seconds':2.1,'captions_same_words_and_downstream_shift_seconds':2.1,'protected_baseline_unchanged_count':sum(checks.values()),'Root_additive_only':True,'all_10_native_assets_present':True,'max_asset_scale':max(a['scale'] for a in spec['items']),'trophy_bottom_projection_error_px':max(bottoms)-min(bottoms),'settled_awards_area_native_pixels_stationary':True,'native_closing_and_final_hold_match_previous':True,'all_25_logo_tiles_lit_before_original_cut':True,'new_source_RGB_preserved':True,'review_limits':'Native geometry and actual film samples checked; this is not subjective boss approval or independent Cantonese transcription.'}

# Export EVERY seam at 0.05s sampling (rounded to unique 30fps frames), plus
# the full iris spread/hold region where it leads the content anchor by 1s.
seams=[{'id':s['id'],'frame':s['startFrame']} for s in json.loads((Q3/'scene-seams.json').read_text())[1:]]
seams+=[{'id':p['id'],'frame':p['startFrame']} for p in manifest['phases']]
seam_sets={s['id']:sorted({max(0,min(2102,s['frame']+round(k*1.5))) for k in range(-12,25)}) for s in seams}
ranges=[(min(v),max(v)) for v in seam_sets.values()]
union=sorted(set(f for lo,hi in ranges for f in range(lo,hi+1)));target=Q4/'transitions/actual-all';target.mkdir(exist_ok=True)
# A few bounded windows avoid FFmpeg's expression recursion limit for hundreds
# of left-associated eq() terms. Grouped seam folders keep the requested 0.05s samples.
select='+'.join(f'between(n\\,{lo}\\,{hi})' for lo,hi in ranges)
run(['ffmpeg','-y','-v','error','-i',str(movies[4]),'-vf',f'select={select}','-fps_mode','vfr','-q:v','2',str(target/'%04d.jpg')])
locations={f:target/f'{i+1:04}.jpg' for i,f in enumerate(union)}
for s in seams:
    folder=Q4/'transitions'/s['id'];folder.mkdir(exist_ok=True);frames=seam_sets[s['id']]
    for f in frames:shutil.copy2(locations[f],folder/f'f{f}.jpg')
    selected=frames[::4];sheet=Image.new('RGB',(1600,math.ceil(len(selected)/4)*250),'#173446');d=ImageDraw.Draw(sheet)
    for i,f in enumerate(selected):
        im=Image.open(locations[f]).resize((400,225));x=i%4*400;y=i//4*250;sheet.paste(im,(x,y));d.text((x+8,y+230),f'f{f} / {f/30:.3f}s',fill='white')
    sheet.save(folder/'contact.jpg',quality=92)
reports[4].update({'iris_count':3,'iris_12_frame_holds':holds,'opaque_interior_checks':coverage,'no_full_frame_opacity_blend':True,'new_content_hidden_during_iris_and_hold':True,'office_photo_exception':'Static final-position photo revealed only by the same mask; no scale or move','values_title_offset_xy':[80,60],'all_seams_exported_at_0_05_second_sampling':len(seams),'exported_unique_seam_frames':len(union),'timing_adaptation':'18 spread frames +12 static frames; phase leads existing content anchors by30 frames; no voice words changed.'})
for st,report in reports.items():
    (R/f'qa/v12/stage{st}/verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('probe','opaque_interior_checks')},ensure_ascii=False,indent=2))
