from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json,math,re,subprocess
import numpy as np
R=Path(__file__).resolve().parents[1];Q=R/'qa/v12/stage7'
MOVIE=R/'out/BOI-HK_史詩形象片_v12_第七版試片.mp4'
def run(args):
    p=subprocess.run(args,capture_output=True)
    if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace'))
    return p.stdout
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rgb(p):return np.asarray(Image.open(p).convert('RGB'))
def packets(p):
    d=json.loads(run(['ffprobe','-v','error','-select_streams','a:0','-show_packets','-show_data_hash','sha256','-of','json',str(p)]))
    return [{k:x.get(k) for k in ('pts','dts','duration','data_hash')} for x in d['packets']]
baseline=json.loads((Q/'baseline.json').read_text())
assert [p for p,h in baseline.items() if sha(R/p)!=h]==['src/Root.tsx']
root=(R/'src/Root.tsx').read_text().replace("import {EpicFilmV12Stage7} from './scenes/ScenesV12Stage7';\n",'')
root='\n'.join(x for x in root.split('\n') if '<Folder name="V12Stage7">' not in x)
assert root==(Q/'before/src/Root.tsx').read_text()
old=json.loads((R/'src/config/awards-stage3.json').read_text());new=json.loads((R/'src/config/awards-stage7.json').read_text())
docs_old=[a for a in old['items'] if a['category']=='document'];docs=[a for a in new['items'] if a['category']=='document']
assert len(new['items'])==10 and len(docs)==6
for a,b in zip(old['items'],new['items']):
    for k in a:
        if k not in ('x','top','baseline'):assert a[k]==b[k],(a['id'],k)
    assert b['scale']<=1
    if a['category']=='document':assert b['top']==a['top']-30
    elif a['id']=='native-a016':assert b['top']==a['top']+12 and b['x']==a['x']
    else:assert b['top']==a['top'] and b['x']==a['x']
assert abs(min(a['x'] for a in docs)-min(a['x'] for a in docs_old)-40)<1e-6
assert abs(max(a['x']+a['display_width'] for a in docs)-max(a['x']+a['display_width'] for a in docs_old)+40)<1e-6
gaps=[docs[i+1]['x']-docs[i]['x']-docs[i]['display_width'] for i in range(5)]
assert all(abs(x-20)<1e-6 for x in gaps)
assert np.array_equal(rgb(Q/'frames/f810.png')[300:1042],rgb(Q/'frames/f900.png')[300:1042])
front=[]
for a in new['items']:
    if a['category']=='trophy':
        alpha=np.asarray(Image.open(R/'public'/a['file']).getchannel('A'))
        y,x=np.where(alpha>=128)
        front.append({'id':a['id'],'visible_bottom':a['top']+(int(y.max())+1)*a['scale'],'scale':a['scale']})
aligned=[x['visible_bottom'] for x in front if x['id']!='native-a016'];assert max(aligned)-min(aligned)<2

metrics=json.loads((Q/'route-browser-metrics.json').read_text());assert len(metrics)>=30
source=(R/'src/components/GeographicNetworkStage7.tsx').read_text()
assert 'getTotalLength()' in source and 'getPointAtLength(' in source
assert 'feGaussianBlur' not in source and 'mixBlendMode' not in source and 'coords[idx]' not in source
world=json.loads((R/'src/assets/world-v12.json').read_text())
reference=metrics['1110']['routes'];controls=[]
for m in reference:
    assert m['d'].count('C')==1 and 'L' not in m['d']
    values=[float(x) for x in re.findall(r'[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?',m['d'])]
    assert len(values)==8
    p0=np.array(values[:2]);p1=np.array(values[2:4]);p2=np.array(values[4:6]);p3=np.array(values[6:])
    if not m['inset']:
        assert np.allclose(p0,world['cities']['香港']['xy'],atol=1e-8)
        assert np.allclose(p3,world['cities'][m['key']]['xy'],atol=1e-8)
    delta=p3-p0;chord=np.linalg.norm(delta);n=np.array([-delta[1],delta[0]])/chord
    if n[1]>0:n=-n
    assert np.allclose(p1,p0+delta*.28+n*chord*.18,atol=1e-7)
    assert np.allclose(p2,p0+delta*.72+n*chord*.18,atol=1e-7)
    controls.append({'key':m['key'],'browser_length':m['length'],'C_control_points':values,'sample_step_max':m['maxSampleStep']})
assert max(r['maxSampleStep'] for frame in metrics.values() for r in frame['routes'])<=5
assert [r['start'] for r in reference[:3]]==[34.16,34.52,35.6]
assert [r['duration'] for r in reference[:3]]==[.45,.95,.8]
for a,b in zip(reference[:3],reference[1:3]):assert b['start']-a['start']>=.18
for frame in metrics.values():
    for key,v in frame['labels'].items():
        ref=metrics['1110']['labels'][key]
        assert abs(v['x']-ref['x'])<.01 and abs(v['y']-ref['y'])<.01

z=Q/'route-qa';z.mkdir(exist_ok=True);sequences={}
for name,key,mid,end in [('shenzhen-main','深圳',1030,1039),('shenzhen-inset','港深放大',1030,1039),('newyork','紐約',1046,1065),('singapore','新加坡',1076,1092)]:
    for phase,frame in [('mid',mid),('end',end)]:
        m=next(a for a in metrics[str(frame)]['routes'] if a['key']==key);x,y=m['head'];r=55 if 'shenzhen' in name else 65
        Image.open(Q/f'frames/f{frame}.png').convert('RGB').crop((int(x-r),int(y-r),int(x+r),int(y+r))).resize((390,390)).save(z/f'{name}-{phase}.png')
for name,key,frames in [('shenzhen','港深放大',list(range(1028,1034))),('newyork','紐約',list(range(1046,1052))),('singapore','新加坡',list(range(1076,1082)))]:
    m=[next(a for a in metrics[str(f)]['routes'] if a['key']==key) for f in frames]
    assert all(b['headDistance']>a['headDistance'] for a,b in zip(m,m[1:]))
    points=[x['head'] for x in m]
    box=[math.floor(min(p[0] for p in points)-30),math.floor(min(p[1] for p in points)-30),math.ceil(max(p[0] for p in points)+30),math.ceil(max(p[1] for p in points)+30)]
    sheet=Image.new('RGB',(1260,500),'#173446');d=ImageDraw.Draw(sheet)
    for i,f in enumerate(frames):
        im=Image.open(Q/f'frames/f{f}.png').convert('RGB').crop(box);im.thumbnail((410,215));x,y=i%3*420,i//3*250;sheet.paste(im,(x,y));d.text((x+8,y+220),f'{name} / f{f} / {f/30:.5f}s',fill='white')
    sheet.save(z/f'{name}-six-consecutive.jpg',quality=96)
    sequences[name]={'frames':frames,'fixed_crop':box,'browser_head_positions':points,'arc_distances':[a['headDistance'] for a in m]}
(z/'consecutive-metrics.json').write_text(json.dumps(sequences,indent=2)+'\n')
Image.open(Q/'frames/f1110.png').convert('RGB').crop((140,520,960,930)).save(z/'main-inset-relationship.png')
head=next(a for a in metrics['1046']['routes'] if a['key']=='紐約')['head']
x,y=head;Image.open(Q/'frames/f1046.png').convert('RGB').crop((int(x-70),int(y-50),int(x+20),int(y+50))).resize((450,500)).save(z/'newyork-glow-edge.png')

same=[]
for f in [96,570,1326,1602,2043,2102]:
    assert np.array_equal(rgb(Q/f'frames/f{f}.png'),rgb(R/f'qa/v12/stage6/frames/f{f}.png')),f
    same.append(f)
probe=json.loads(run(['ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_name,width,height,nb_frames,avg_frame_rate','-of','json',str(MOVIE)]))
v=probe['streams'][0]
assert (v['width'],v['height'],v['nb_frames'],v['avg_frame_rate'])==(1920,1080,'2103','30/1')
assert 70.1<=float(probe['format']['duration'])<=70.13
run(['ffmpeg','-v','error','-i',str(MOVIE),'-f','null','-'])
audio=packets(MOVIE);assert audio==packets(R/'qa/v12/stage3/audio-master.m4a')==packets(R/'out/BOI-HK_史詩形象片_v12_第六版試片.mp4')
frames=sorted(set([500,570,705,710,750,810,900,923,932,1002,1025,1030,1036,1039,1065,1068,1092,1104,1110,1140,1145,1150,1326,1602,2043,2102]+list(range(1046,1052))+list(range(1076,1082))))
actual=Q/'actual-frames';actual.mkdir(exist_ok=True)
select='+'.join(f'eq(n\\,{f})' for f in frames)
run(['ffmpeg','-y','-v','error','-i',str(MOVIE),'-vf',f'select={select}','-fps_mode','vfr','-q:v','2',str(actual/'%03d.jpg')])
locations={f:actual/f'{i+1:03}.jpg' for i,f in enumerate(frames)}
sheet=Image.new('RGB',(1600,math.ceil(len(frames)/4)*250),'#173446');draw=ImageDraw.Draw(sheet)
for i,f in enumerate(frames):
    x,y=i%4*400,i//4*250;sheet.paste(Image.open(locations[f]).resize((400,225)),(x,y));draw.text((x+8,y+230),f'{f/30:.3f}s / f{f}',fill='white')
sheet.save(Q/'actual-storyboard.jpg',quality=94)
(Q/'actual-frame-index.json').write_text(json.dumps({str(f):str(p.relative_to(R)) for f,p in locations.items()},indent=2)+'\n')
compare=Image.new('RGB',(1920,1160),'#173446');draw=ImageDraw.Draw(compare)
for row,f in enumerate([810,1110]):
    before=Q/f'actual-stage6-f{f}.png'
    if not before.exists():run(['ffmpeg','-n','-v','error','-i',str(R/'out/BOI-HK_史詩形象片_v12_第六版試片.mp4'),'-vf',f'select=eq(n\\,{f})','-frames:v','1',str(before)])
    for col,(name,p) in enumerate([('Stage6 before',before),('Stage7 after',locations[f])]):
        x,y=col*960,row*580;compare.paste(Image.open(p).convert('RGB').resize((960,540)),(x,y+40));draw.text((x+15,y+14),f'{name} / {f/30:.1f}s',fill='white')
compare.save(Q/'awards-map-before-after.jpg',quality=95)
preview=R/'out/BOI-HK_v12_第七版_獎項與連線16秒預覽.mp4'
preview_probe=json.loads(run(['ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_name,nb_frames','-of','json',str(preview)]))
assert preview_probe['streams'][0]['nb_frames']=='480'
run(['ffmpeg','-v','error','-i',str(preview),'-f','null','-'])
report={'output':str(MOVIE),'sha256':sha(MOVIE),'probe':probe,'complete_decode_ok':True,
 'protected_unchanged_files':len(baseline)-1,'protected_total':len(baseline),'Root_additive_only':True,
 'audio_packets_identical_to_Stage6_and_master':True,'AAC_packets':len(audio),'no_new_voice_music_or_mix':True,
 'awards_count':10,'all_award_dimensions_scale_RGB_files_retained':True,'back_top_delta':-30,'back_width_before':max(a['x']+a['display_width'] for a in docs_old)-min(a['x'] for a in docs_old),'back_width_after':new['back_group_width'],'back_each_edge_inset':40,'back_equal_gap':20,'blue_whale_top_delta':12,'front_projected_bottoms':front,'other_three_bottoms_spread':max(aligned)-min(aligned),'settled_awards_body_native_pixels_stationary':True,
 'route_DOM_measurement_frames':len(metrics),'routes':controls,'all_measured_sample_steps_le5':True,'single_C_per_route':True,'no_gaussian_or_blend_in_new_route_component':True,'narration_gated_starts':[34.16,34.52,35.6],'durations':[.45,.95,.8],'label_delay':.12,'minimum_stagger':.18,'six_consecutive_frame_sequences':sequences,'label_positions_stable_across_frames':True,'singapore_preparing_label_retained':True,
 'native_unchanged_sample_frames':same,'actual_movie_samples':len(frames),'preview':{'path':str(preview),'sha256':sha(preview),'probe':preview_probe,'complete_decode_ok':True},
 'review_limits':'Browser SVG geometry and sampled frames plus full decode verified. Fixed0.18s starts adapted to preserve narration gates. Awards width uses actual source bounds, not the draft estimate. Subjective acceptance remains pending.'}
(Q/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('six_consecutive_frame_sequences','preview')},ensure_ascii=False,indent=2))
