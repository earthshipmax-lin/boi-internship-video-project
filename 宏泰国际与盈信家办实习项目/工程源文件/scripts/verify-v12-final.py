from pathlib import Path
import hashlib
import json
import subprocess
from PIL import Image, ImageDraw

V = Path(__file__).resolve().parents[1]
Q = V / 'qa/v12/final'
MOVIE = V / 'out/BOI-HK_史詩形象片_v12_定版審片.mp4'
OLD = V / 'out/BOI-HK_史詩形象片_v12_第八版試片.mp4'
PREVIEW = V / 'out/BOI-HK_v12_定版審片_新增畫面17秒預覽.mp4'


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
assert pcm == pcm_hash(OLD)
audit = json.loads((Q / 'review-frame-audit.json').read_text())
assert sorted(map(int, audit)) == list(range(2103)), f'Missing frame audits: {set(range(2103))-set(map(int,audit))}'
cues = json.loads((V / 'src/config/captions-v12-stage3.json').read_text())
for f, a in audit.items():
    time = min(int(f) / 30, 68.1)
    expected = next((c['text'] for c in cues if c['start'] <= time < c['end'] + .12), '')
    assert a['caption'] == expected, (f, a['caption'], expected)
    assert a['captionStyle'] == {'bottom': '58px', 'left': '105px', 'right': '105px', 'fontSize': '36px', 'textAlign': 'center'}
    assert a['watermark']
    assert not any(s in a['text'] for s in ['據公司', '据公司', '資料來源', '资料来源', '免責', '免责'])
    assert all(m['top'] == '94px' and m['right'] == '112px' and m['fontSize'] == '20px' for m in a['metas'])
base = json.loads((Q / 'baseline.json').read_text())
changed = [p for p, h in base.items() if sha(V / p) != h]
assert changed == ['src/Root.tsx'], changed
root = (V / 'src/Root.tsx').read_text()
root = root.replace("import {EpicFilmV12Final} from './scenes/ScenesV12Final';\n", '')
root = root.replace(' <Folder name="V12Final"><Composition id="BOI-HK-Epic-v12-Final" component={EpicFilmV12Final} width={1920} height={1080} fps={30} durationInFrames={2103} defaultProps={{watermark:true,qa:false}}/></Folder>\n', '')
assert root == (Q / 'before/src/Root.tsx').read_text()
offices = json.loads((V / 'src/config/offices-final.json').read_text())
for a in offices:
    assert a['cover_scale'] <= 1
    assert sha(V / 'public' / a['file']) == a['sha256'] == sha(Path(a['pdf_native']))
assert not (V / 'out/BOI-HK_史詩形象片_v12_乾淨母版.mp4').exists()
assert not (Q / 'video-only-clean.mp4').exists()
subprocess.run(['ffmpeg', '-v', 'error', '-n', '-ss', '38', '-i', str(MOVIE), '-t', '17.1',
                '-map', '0:v:0', '-map', '0:a:0', '-c:v', 'libx264', '-crf', '18', '-preset', 'fast',
                '-c:a', 'copy', '-movflags', '+faststart', str(PREVIEW)], check=True)
decode(PREVIEW)
actual = Q / 'actual-frames'
actual.mkdir(exist_ok=True)
frames = [96, 500, 570, 650, 810, 1050, 1110, 1200, 1224, 1230, 1260, 1323, 1336, 1358, 1359,
          1364, 1365, 1383, 1398, 1401, 1414, 1440, 1476, 1485, 1500, 1563, 1564, 1580, 1602, 1644, 1652, 1700, 2043, 2102]
for f in frames:
    extract(MOVIE, f, actual / f'f{f}.png')
for f in [1260, 1440, 1602]:
    extract(OLD, f, actual / f'before-f{f}.png')
sheet = Image.new('RGB', (1440, ((len(frames) + 2) // 3) * 295), '#172630')
d = ImageDraw.Draw(sheet)
for i, f in enumerate(frames):
    im = Image.open(actual / f'f{f}.png').resize((480, 270))
    x, y = i % 3 * 480, i // 3 * 295
    sheet.paste(im, (x, y))
    d.text((x + 8, y + 275), f'{f/30:.3f}s / f{f}', fill='white')
sheet.save(Q / 'actual-overview.jpg', quality=92)
comparison = Image.new('RGB', (1920, 1710), '#172630')
d = ImageDraw.Draw(comparison)
for row, f in enumerate([1260, 1440, 1602]):
    for col, prefix in enumerate(['before-', '']):
        im = Image.open(actual / f'{prefix}f{f}.png').resize((960, 540))
        comparison.paste(im, (col * 960, row * 570 + 30))
        d.text((col * 960 + 12, row * 570 + 8), f'{"Stage8 BEFORE" if col == 0 else "Prompt10 AFTER"} / {f/30:.1f}s', fill='white')
comparison.save(Q / 'before-after.jpg', quality=93)
verification = {'output': str(MOVIE), 'sha256': sha(MOVIE), 'probe': info, 'full_decode': True,
                'audio_packets': len(audio), 'audio_packets_and_timestamps_equal': True, 'pcm_equal_to_stage8': pcm,
                'protected_files_unchanged': len(base) - 1, 'protected_total': len(base), 'root_additive_only': True,
                'frame_DOM_audit_count': len(audit), 'caption_content_cue_and_geometry_all_frames_verified': True,
                'forbidden_strings_DOM_hits': [], 'meta_geometry_uniform': True, 'watermark_all_frames': True,
                'new_offices': offices, 'clean_master_not_rendered': True,
                'actual_movie_frames': frames,
                'preview': {'path': str(PREVIEW), 'sha256': sha(PREVIEW), 'probe': probe(PREVIEW), 'full_decode': True},
                'limits': 'DOM audit is exhaustive for rendered text; also run encoded-frame OCR for image text. Visual and listening acceptance remain pending.'}
(Q / 'verification.json').write_text(json.dumps(verification, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'movie': str(MOVIE), 'sha256': sha(MOVIE), 'audio_packets': len(audio), 'PCM': pcm,
                  'frame_audit': len(audit), 'preview': str(PREVIEW)}, ensure_ascii=False, indent=2))
