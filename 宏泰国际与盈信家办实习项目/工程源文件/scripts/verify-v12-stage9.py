from pathlib import Path
import hashlib
import json
import subprocess
from PIL import Image, ImageDraw

V = Path(__file__).resolve().parents[1]
Q = V / 'qa/v12/stage9'
MOVIE = V / 'out/BOI-HK_史詩形象片_v12_第九版試片.mp4'
OLD = V / 'out/BOI-HK_史詩形象片_v12_三城辦公室試片.mp4'
PREVIEW = V / 'out/BOI-HK_v12_第九版_三鏡精修22秒預覽.mp4'


def run(args):
    return subprocess.check_output(args, text=True)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def probe(p):
    return json.loads(run(['ffprobe', '-v', 'error', '-show_entries',
                          'format=duration,size:stream=codec_name,width,height,avg_frame_rate,nb_frames', '-of', 'json', str(p)]))


def packets(p):
    return json.loads(run(['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_packets',
                          '-show_data_hash', 'sha256', '-show_entries', 'packet=pts,dts,duration,data_hash', '-of', 'json', str(p)]))['packets']


def pcm_hash(p):
    proc = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', str(p), '-map', '0:a:0',
                             '-f', 'f32le', '-acodec', 'pcm_f32le', '-'], stdout=subprocess.PIPE)
    digest = hashlib.sha256()
    count = 0
    while block := proc.stdout.read(1024 * 1024):
        digest.update(block)
        count += len(block)
    assert proc.wait() == 0
    return {'sha256': digest.hexdigest(), 'f32le_bytes': count}


def decode(p):
    subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(p), '-f', 'null', '-'], check=True)


def extract(p, f, target):
    subprocess.run(['ffmpeg', '-v', 'error', '-i', str(p), '-vf', f'select=eq(n\\,{f})',
                    '-frames:v', '1', '-update', '1', '-y', str(target)], check=True)


def overlap(a,b):
    return min(a['x']+a['width'],b['x']+b['width'])>max(a['x'],b['x'])+.01 and min(a['y']+a['height'],b['y']+b['height'])>max(a['y'],b['y'])+.01


info=probe(MOVIE)
assert info['streams'][0]['nb_frames']=='2103' and info['format']['duration']=='70.100000'
decode(MOVIE)
audio=packets(MOVIE)
assert audio==packets(OLD)==packets(V/'qa/v12/stage3/audio-master.m4a')
pcm=pcm_hash(MOVIE)
assert pcm==pcm_hash(OLD)
audit=json.loads((Q/'review-frame-audit.json').read_text())
assert sorted(map(int,audit))==list(range(2103))
cues=json.loads((V/'src/config/captions-v12-stage3.json').read_text())
awards_checks=[];platform_checks=[]
for f,a in audit.items():
    frame=int(f);time=min(frame/30,68.1)
    expected=next((c['text'] for c in cues if c['start']<=time<c['end']+.12),'')
    assert a['caption']==expected,(f,a['caption'],expected)
    assert a['root']=={'width':1920,'height':1080}
    assert a['captionRect']=={'x':105,'y':967,'width':1710,'height':55}
    assert a['watermark']
    assert not any(w in a['text'] for w in ['據公司','据公司','資料來源','资料来源','免責','免责'])
    if 864<=frame<1359:assert not a['awards'],f
    if 729<=frame<864:
        trophies=[p for p in a['awards'] if p['layer']=='trophy']
        assert len(trophies)==4
        bottoms=[p['rect']['y']+p['rect']['height'] for p in trophies]
        assert max(bottoms)-min(bottoms)<=2
        assert all(float(p['opacity'])==1 for p in trophies)
        awards_checks.append({'frame':frame,'bottom_spread':max(bottoms)-min(bottoms)})
    if 1141<=frame<1323:
        title=next(p for p in a['platform'] if p['role']=='title')
        for p in a['platform']:
            if p['role']=='title' or float(p['opacity'])==0:continue
            assert not overlap(title['rect'],p['rect']),(f,p['role'],p['rect'],title['rect'])
            assert p['rect']['y']+p['rect']['height']<967,(f,p['role'])
        platform_checks.append({'frame':frame,'title_rect':title['rect'],'elements':len(a['platform'])})
subprocess.run(['python3',str(V/'scripts/check-stage9-routes.py'),str(Q/'review-routes.json'),str(Q/'routes-check.json')],check=True)
geometry=json.loads((Q/'platform-geometry.json').read_text())
assert all(abs(s['nominalDegrees']-120)<=1 and abs(s['drawnDegrees']-114)<=1 for s in geometry['sectors'])
nodes=geometry['nodes'];lengths=[]
for n in nodes:
    import math
    assert abs(math.hypot(n['point']['x']-geometry['center']['x'],n['point']['y']-geometry['center']['y'])-geometry['outerRadius'])<.01
    assert abs(math.hypot(n['point']['x']-n['branchStart']['x'],n['point']['y']-n['branchStart']['y'])-60)<.01
for i,n in enumerate(nodes):
    m=nodes[(i+1)%5];lengths.append(math.hypot(n['point']['x']-m['point']['x'],n['point']['y']-m['point']['y']))
assert max(lengths)-min(lengths)<=2
base=json.loads((Q/'baseline.json').read_text())
assert [f for f,h in base.items() if sha(V/f)!=h]==['src/Root.tsx']
root=(V/'src/Root.tsx').read_text().replace("import {EpicFilmV12Stage9} from './scenes/ScenesV12Stage9';\n",'')
root=root.replace(' <Folder name="V12Stage9"><Composition id="BOI-HK-Epic-v12-Stage9" component={EpicFilmV12Stage9} width={1920} height={1080} fps={30} durationInFrames={2103} defaultProps={{watermark:true,qa:false}}/></Folder>\n','')
assert root==(Q/'before/src/Root.tsx').read_text()
# The platform, including its annual-ring background, truly stops at2.8s.
platform_roi=(550,380,1340,940)
stable=Image.open(Q/'frames/f1225.png').crop(platform_roi).tobytes()
assert all(Image.open(Q/f'frames/f{f}.png').crop(platform_roi).tobytes()==stable for f in [1250,1280,1322])
subprocess.run(['ffmpeg','-v','error','-n','-ss','23.5','-i',str(MOVIE),'-t','21.8','-map','0:v:0','-map','0:a:0','-c:v','libx264','-crf','18','-preset','fast','-c:a','copy','-movflags','+faststart',str(PREVIEW)],check=True)
decode(PREVIEW)
actual=Q/'actual-frames';actual.mkdir(exist_ok=True)
frames=[716,729,741,742,743,744,780,863,864,888,948,1070,1071,1072,1073,1096,1097,1098,1099,1140,1150,1177,1200,1225,1250,1280,1322,1323,1336,1358,1517,1602]
for f in frames:extract(MOVIE,f,actual/f'f{f}.png')
for f in [863,1071,1250]:extract(OLD,f,actual/f'before-f{f}.png')
sheet=Image.new('RGB',(1440,((len(frames)+2)//3)*295),'#182630');d=ImageDraw.Draw(sheet)
for i,f in enumerate(frames):
    x,y=i%3*480,i//3*295;sheet.paste(Image.open(actual/f'f{f}.png').resize((480,270)),(x,y));d.text((x+10,y+274),f'{f/30:.3f}s / {f}',fill='white')
sheet.save(Q/'actual-overview.jpg',quality=92)
comparison=Image.new('RGB',(1920,1710),'#182630');d=ImageDraw.Draw(comparison)
for row,f in enumerate([863,1071,1250]):
    for col,prefix in enumerate(['before-','']):
        comparison.paste(Image.open(actual/f'{prefix}f{f}.png').resize((960,540)),(col*960,row*570+30));d.text((col*960+12,row*570+8),f'{"Offices BEFORE" if col==0 else "Stage9 AFTER"} / {f/30:.3f}s',fill='white')
comparison.save(Q/'before-after.jpg',quality=93)
(Q/'three-scene-geometry-check.json').write_text(json.dumps({'award_frames':awards_checks,'platform_frames':platform_checks,'sector_nominal_angles':[s['nominalDegrees'] for s in geometry['sectors']],'node_neighbor_chords':lengths,'node_chord_spread':max(lengths)-min(lengths),'platform_static_roi':platform_roi,'platform_static_frames':[1225,1250,1280,1322]},indent=2)+'\n')
result={'output':str(MOVIE),'sha256':sha(MOVIE),'probe':info,'full_decode':True,'audio_packets':len(audio),'audio_packet_payload_timestamps_equal':True,'pcm_equal_to_Offices':pcm,'full_DOM_frames':len(audit),'captions_cues_geometry_equal':True,'award_cut_exact':864,'award_baseline_max_spread':max(a['bottom_spread'] for a in awards_checks),'routes':'routes-check.json','platform_static_from':2.8,'geometry_checks':'three-scene-geometry-check.json','protected_unchanged':len(base)-1,'protected_total':len(base),'root_additive_only':True,'actual_samples':frames,'preview':{'path':str(PREVIEW),'sha256':sha(PREVIEW),'probe':probe(PREVIEW),'full_decode':True},'limits':'Locked audio/cues take precedence over draft guessed starts. Motion/background/static distinctions and geometric adaptations are documented in IMPLEMENTATION.md. Visual acceptance pending.'}
(Q/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['output','sha256','audio_packets','full_DOM_frames','award_cut_exact','award_baseline_max_spread','protected_unchanged']},ensure_ascii=False,indent=2))
