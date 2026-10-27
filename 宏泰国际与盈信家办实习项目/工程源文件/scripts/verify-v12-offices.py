from pathlib import Path
import hashlib
import json
import subprocess
from PIL import Image, ImageDraw

V = Path(__file__).resolve().parents[1]
Q = V / 'qa/v12/offices'
MOVIE = V / 'out/BOI-HK_史詩形象片_v12_三城辦公室試片.mp4'
OLD = V / 'out/BOI-HK_史詩形象片_v12_定版審片.mp4'
PREVIEW = V / 'out/BOI-HK_v12_三城辦公室與分屏11秒預覽.mp4'


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


info = probe(MOVIE)
assert info['streams'][0]['nb_frames'] == '2103'
assert info['format']['duration'] == '70.100000'
decode(MOVIE)
audio = packets(MOVIE)
assert audio == packets(OLD) == packets(V / 'qa/v12/stage3/audio-master.m4a')
pcm = pcm_hash(MOVIE)
assert pcm == pcm_hash(OLD) == pcm_hash(V / 'out/BOI-HK_史詩形象片_v12_第八版試片.mp4')
audit = json.loads((Q / 'review-frame-audit.json').read_text())
assert sorted(map(int, audit)) == list(range(2103))
cues = json.loads((V / 'src/config/captions-v12-stage3.json').read_text())
for f, a in audit.items():
    time = min(int(f) / 30, 68.1)
    expected = next((c['text'] for c in cues if c['start'] <= time < c['end'] + .12), '')
    assert a['caption'] == expected, (f, a['caption'], expected)
    assert a['watermark']
    assert not any(s in a['text'] for s in ['據公司', '据公司', '資料來源', '资料来源', '免責', '免责'])
subprocess.run(['python3', str(V / 'scripts/check-office-bounds.py'), str(Q / 'review-frame-audit.json'), str(Q / 'bounding-check.json')], check=True)
base = json.loads((Q / 'baseline.json').read_text())
assert [f for f, h in base.items() if sha(V / f) != h] == ['src/Root.tsx']
root = (V / 'src/Root.tsx').read_text().replace("import {EpicFilmV12Offices} from './scenes/ScenesV12Offices';\n", '')
root = root.replace(' <Folder name="V12Offices"><Composition id="BOI-HK-Epic-v12-Offices" component={EpicFilmV12Offices} width={1920} height={1080} fps={30} durationInFrames={2103} defaultProps={{watermark:true,qa:false}}/></Folder>\n', '')
assert root == (Q / 'before/src/Root.tsx').read_text()
asset_config = json.loads((V / 'src/config/offices-assets-v12.json').read_text())
for city in asset_config['cities']:
    for a in city['images']:
        assert a['maximum_display_scale'] <= 1
        dst, src = V / 'public' / a['file'], V / a['source']
        assert sha(dst) == a['output_sha256']
        assert sha(src) == a['source_sha256']
        crop = Image.open(src).crop(a['crop']).convert('RGBA')
        assert crop.tobytes() == Image.open(dst).convert('RGBA').tobytes()
assert not (V / 'out/BOI-HK_史詩形象片_v12_三城辦公室_乾淨母版.mp4').exists()
native_static = {}
for start, end, city in [(1383,1425,'香港'), (1450,1492,'深圳'), (1517,1559,'紐約')]:
    a = Image.open(Q / f'frames/f{start}.png').crop((130,300,1790,900))
    b = Image.open(Q / f'frames/f{end}.png').crop((130,300,1790,900))
    assert a.tobytes() == b.tobytes(), city
    native_static[city] = {'start': start, 'end_inclusive': end, 'frames': end-start+1, 'seconds': (end-start+1)/30, 'native_first_last_pixels_equal': True}
subprocess.run(['ffmpeg', '-v', 'error', '-n', '-ss', '44.1', '-i', str(MOVIE), '-t', '11',
                '-map', '0:v:0', '-map', '0:a:0', '-c:v', 'libx264', '-crf', '18', '-preset', 'fast',
                '-c:a', 'copy', '-movflags', '+faststart', str(PREVIEW)], check=True)
decode(PREVIEW)
assert probe(PREVIEW)['streams'][0]['nb_frames'] == '330'
actual = Q / 'actual-frames'
actual.mkdir(exist_ok=True)
frames = [1358,1359,1369,1383,1425,1426,1436,1450,1492,1493,1503,1517,1559,1560,1564,1568,1569,1575,1587,1602,1644,1652]
for f in frames:
    extract(MOVIE, f, actual / f'f{f}.png')
for f in [1450,1517,1602]:
    extract(OLD, f, actual / f'before-f{f}.png')
    if f not in frames:
        extract(MOVIE, f, actual / f'f{f}.png')
sheet = Image.new('RGB', (1440, ((len(frames)+2)//3)*295), '#182630')
d = ImageDraw.Draw(sheet)
for i, f in enumerate(frames):
    im = Image.open(actual / f'f{f}.png').resize((480,270))
    x, y = i%3*480, i//3*295
    sheet.paste(im,(x,y));d.text((x+10,y+274),f'{f/30:.3f}s / {f}',fill='white')
sheet.save(Q/'actual-overview.jpg',quality=92)
comparison = Image.new('RGB',(1920,1710),'#182630')
d = ImageDraw.Draw(comparison)
for row, f in enumerate([1450,1517,1602]):
    for col,prefix in enumerate(['before-','']):
        im=Image.open(actual/f'{prefix}f{f}.png').resize((960,540))
        comparison.paste(im,(col*960,row*570+30))
        d.text((col*960+12,row*570+8),f'{"Prompt10 BEFORE" if col==0 else "Prompt11 AFTER"} / {f/30:.3f}s',fill='white')
comparison.save(Q/'before-after.jpg',quality=93)
verification={'output':str(MOVIE),'sha256':sha(MOVIE),'probe':info,'full_decode':True,
              'audio_packets':len(audio),'audio_packets_and_timestamps_equal_to_Final_and_master':True,
              'pcm_equal_to_Final_and_Stage8':pcm,'protected_files_unchanged':len(base)-1,'protected_total':len(base),'root_additive_only':True,
              'DOM_frames':len(audit),'captions_and_cues_all_frames_equal':True,'forbidden_DOM_hits':[],
              'bounding':'bounding-check.json','static_windows':native_static,'all_nine_sources_and_crops_verified':True,
              'maximum_photo_scale':max(a['maximum_display_scale'] for c in asset_config['cities'] for a in c['images']),
              'clean_master_not_rendered':True,'actual_movie_sample_frames':frames,
              'preview':{'path':str(PREVIEW),'sha256':sha(PREVIEW),'probe':probe(PREVIEW),'full_decode':True},
              'limits':'DOM geometry includes mask clipping, not glyph ink segmentation. Subjective acceptance remains pending; encoded OCR scope recorded separately.'}
(Q/'verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'movie':str(MOVIE),'sha256':sha(MOVIE),'DOM_frames':len(audit),'static_windows':native_static,'audio_packets':len(audio),'PCM':pcm},ensure_ascii=False,indent=2))
