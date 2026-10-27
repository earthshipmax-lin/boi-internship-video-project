from pathlib import Path
import hashlib
import json
import subprocess
from PIL import Image, ImageDraw

V = Path(__file__).resolve().parents[1]
Q = V / 'qa/v12/stage8'
MOVIE = V / 'out/BOI-HK_史詩形象片_v12_第八版試片.mp4'
PREVIOUS = V / 'out/BOI-HK_史詩形象片_v12_第七版試片.mp4'
PREVIEW = V / 'out/BOI-HK_v12_第八版_獎項字幕修復10秒預覽.mp4'


def run(args):
    return subprocess.check_output(args, text=True)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def probe(p):
    return json.loads(run(['ffprobe', '-v', 'error', '-show_entries',
                          'format=duration,size:stream=codec_name,width,height,avg_frame_rate,nb_frames',
                          '-of', 'json', str(p)]))


def packets(p):
    return json.loads(run(['ffprobe', '-v', 'error', '-select_streams', 'a:0',
                          '-show_packets', '-show_data_hash', 'sha256', '-show_entries',
                          'packet=pts,dts,duration,data_hash', '-of', 'json', str(p)]))['packets']


def decode(p):
    subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(p), '-f', 'null', '-'], check=True)


def extract(p, frame, target):
    subprocess.run(['ffmpeg', '-v', 'error', '-i', str(p), '-vf', f'select=eq(n\\,{frame})',
                    '-frames:v', '1', '-update', '1', '-y', str(target)], check=True)


decode(MOVIE)
info = probe(MOVIE)
assert info['streams'][0]['nb_frames'] == '2103'
assert info['format']['duration'] == '70.100000'
audio = packets(MOVIE)
assert audio == packets(PREVIOUS) == packets(V / 'qa/v12/stage3/audio-master.m4a')
assert len(audio) == 3287
subprocess.run(['ffmpeg', '-v', 'error', '-ss', '23', '-i', str(MOVIE), '-t', '10',
                '-map', '0:v:0', '-map', '0:a:0', '-c:v', 'libx264', '-crf', '18',
                '-preset', 'fast', '-c:a', 'copy', '-movflags', '+faststart', str(PREVIEW)], check=True)
decode(PREVIEW)
actual = Q / 'actual-frames'
actual.mkdir(exist_ok=True)
frames = [704, 710, 735, 750, 770, 810, 838, 840, 843, 900, 922, 926, 931, 932]
for f in frames:
    extract(MOVIE, f, actual / f'f{f}.png')
extract(PREVIOUS, 810, actual / 'previous-f810.png')
comparison = Image.new('RGB', (1920, 1120), '#15232c')
d = ImageDraw.Draw(comparison)
for i, name in enumerate(['previous-f810.png', 'f810.png']):
    im = Image.open(actual / name).convert('RGB').resize((960, 540))
    comparison.paste(im, (i * 960, 30))
    d.text((i * 960 + 20, 10), ['BEFORE: Stage7 / 27s', 'AFTER: Stage8 / 27s'][i], fill='white')
for i, f in enumerate([750, 810, 843, 932]):
    im = Image.open(actual / f'f{f}.png').resize((480, 270))
    comparison.paste(im, (i * 480, 600))
    d.text((i * 480 + 10, 880), f'{f/30:.3f}s | frame {f}', fill='white')
# Crop actual encoded frames to inspect the consistent caption lane at full size.
comparison.paste(Image.open(actual / 'f810.png').crop((420, 940, 1500, 1060)), (420, 930))
comparison.save(Q / 'before-after.jpg', quality=94)
sheet = Image.new('RGB', (1440, 1475), '#15232c')
d = ImageDraw.Draw(sheet)
for i, f in enumerate(frames):
    im = Image.open(actual / f'f{f}.png').resize((480, 270))
    x, y = (i % 3) * 480, (i // 3) * 295
    sheet.paste(im, (x, y))
    d.text((x + 10, y + 273), f'{f/30:.3f}s | frame {f}', fill='white')
sheet.save(Q / 'actual-sequence.jpg', quality=92)
layout = json.loads((Q / 'layout-verification.json').read_text())
verification = {
    'output': str(MOVIE), 'sha256': sha(MOVIE), 'probe': info,
    'complete_decode_ok': True, 'AAC_packets': len(audio),
    'audio_payload_pts_dts_duration_identical_to_Stage7_and_master': True,
    'actual_movie_sample_frames': frames, 'layout': layout,
    'preview': {'path': str(PREVIEW), 'sha256': sha(PREVIEW), 'probe': probe(PREVIEW), 'complete_decode_ok': True},
    'review_limits': 'Code, native stills, sampled encoded frames and full decode checked; subjective design and listening approval remain with user.'
}
(Q / 'verification.json').write_text(json.dumps(verification, ensure_ascii=False, indent=2) + '\n')
source_files = ['src/Root.tsx', 'src/scenes/ScenesV12Stage8.tsx', 'src/components/AwardsStage8.tsx',
                'src/config/awards-stage8.json', 'scripts/render-v12-stage8.mjs', 'scripts/verify-v12-stage8.py']
manifest = {'updated': '2026-10-23', 'composition': 'BOI-HK-Epic-v12-Stage8',
            'source_files': {s: sha(V / s) for s in source_files},
            'movie': {'path': str(MOVIE), 'sha256': sha(MOVIE)},
            'preview': verification['preview'], 'review_status': 'pending_user_playback'}
(Q / 'delivery-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'movie': str(MOVIE), 'sha256': sha(MOVIE), 'AAC_packets': len(audio),
                  'preview': str(PREVIEW), 'decoded': True}, ensure_ascii=False, indent=2))
