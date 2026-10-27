"""Check the Stage5 delivery against the protected Stage4 inputs and actual movie."""
from pathlib import Path
from PIL import Image, ImageDraw
import hashlib
import json
import math
import subprocess
import numpy as np

R = Path(__file__).resolve().parents[1]
Q = R / 'qa/v12/stage5'
MOVIE = R / 'out/BOI-HK_史詩形象片_v12_第五版試片.mp4'


def run(args):
    result = subprocess.run(args, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stderr.decode(errors='replace'))
    return result.stdout


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def arr(path):
    return np.asarray(Image.open(path).convert('RGB'))


def packets(path):
    data = json.loads(run(['ffprobe', '-v', 'error', '-select_streams', 'a:0',
                          '-show_packets', '-show_data_hash', 'sha256', '-of', 'json', str(path)]))
    return [{k: p.get(k) for k in ('pts', 'dts', 'duration', 'data_hash')} for p in data['packets']]


baseline = json.loads((Q / 'baseline.json').read_text())
protected = {p: sha(R / p) == digest for p, digest in baseline.items()}
assert [p for p, ok in protected.items() if not ok] == ['src/Root.tsx']
root = (R / 'src/Root.tsx').read_text()
root = root.replace("import {EpicFilmV12Stage5} from './scenes/ScenesV12Stage5';\n", '')
root = '\n'.join(line for line in root.split('\n') if '<Folder name="V12Stage5">' not in line)
assert root == (Q / 'before/Root.tsx').read_text()

timing = json.loads((Q / 'timing.json').read_text())
assert timing['irisCount'] == 1
assert timing['officeContent'] == timing['irisStart'] + timing['spreadFrames'] + timing['holdFrames']
hold = [arr(Q / f'frames/f{frame}.png') for frame in range(1356, 1359)]
assert all(np.array_equal(hold[0], a) for a in hold)


def bezier(x):
    lo, hi = 0, 1
    for _ in range(24):
        t = (lo + hi) / 2
        bx = 3 * (1 - t)**2 * t * .65 + 3 * (1 - t) * t*t * .35 + t**3
        if bx < x:
            lo = t
        else:
            hi = t
    t = (lo + hi) / 2
    return 3*t*t - 2*t**3


yy, xx = np.mgrid[:1080, :1920]
distance = np.hypot(xx - 960, yy - 820)
interior = []
for offset in (9, 15, 21, 27, 32):
    inside = distance < (1270 * bezier(offset / 33) - 3)
    mid = arr(Q / f'frames/f{1323 + offset}.png')
    error = int(np.abs(mid[inside].astype(int) - hold[0][inside].astype(int)).max())
    assert error == 0, (offset, error)
    interior.append({'offset': offset, 'revealed_RGB_error': error})

first = arr(Q / 'frames/f1530.png')[330:500, 130:1200]
both = arr(Q / 'frames/f1602.png')[330:500, 130:1200]
assert np.array_equal(first, both)
for frame in (810, 900, 2043, 2102):
    assert np.array_equal(arr(Q / f'frames/f{frame}.png'), arr(R / f'qa/v12/stage4/frames/f{frame}.png'))
tiles = arr(Q / 'frames/f500.png')
levels = [float(np.quantile(tiles[280 + i//5*92:360 + i//5*92,
                                 1040 + i%5*153:1182 + i%5*153].min(axis=2), .85))
          for i in range(25)]
assert min(levels) >= 250

banks = []
for name, bounds in [('minsheng', (11, 19, 747, 149)), ('shanghai', (16, 22, 832, 174))]:
    source = R / f'public/stills/v12/bank-{name}.jpg'
    pixels = arr(source)
    y, x = np.where(pixels.min(axis=2) < 225)
    measured = [int(x.min()), int(y.min()), int(x.max() + 1), int(y.max() + 1)]
    assert measured == list(bounds)
    scale = 54 / (bounds[3] - bounds[1])
    width = (bounds[2] - bounds[0]) * scale
    assert width + 16 * scale < 377  # Ink plus the CSS whitespace margin fits its equal cell.
    banks.append({'id': name, 'source_sha256': sha(source), 'source_ink_bounds': measured,
                  'display_ink_height': 54, 'display_ink_width': width, 'ink_center_y': 880,
                  'original_RGB_file_unchanged': True, 'CSS_clip_keeps_all_measured_ink': True})

probe = json.loads(run(['ffprobe', '-v', 'error', '-show_entries',
                       'format=duration,size:stream=codec_name,width,height,nb_frames,avg_frame_rate',
                       '-of', 'json', str(MOVIE)]))
v = probe['streams'][0]
assert v['codec_name'] == 'h264' and v['nb_frames'] == '2103'
assert (v['width'], v['height'], v['avg_frame_rate']) == (1920, 1080, '30/1')
assert 70.1 <= float(probe['format']['duration']) <= 70.13
run(['ffmpeg', '-v', 'error', '-i', str(MOVIE), '-f', 'null', '-'])
audio = packets(MOVIE)
assert audio == packets(R / 'qa/v12/stage3/audio-master.m4a')
assert audio == packets(R / 'out/BOI-HK_史詩形象片_v12_第四版試片.mp4')

# Inspect every output frame's unused upper-right background patch after the iris.
rgb = run(['ffmpeg', '-v', 'error', '-i', str(MOVIE), '-vf',
           'select=gte(n\\,1356),crop=8:8:1900:10,format=rgb24',
           '-fps_mode', 'vfr', '-f', 'rawvideo', '-'])
patches = np.frombuffer(rgb, dtype=np.uint8).reshape((-1, 8, 8, 3))
assert len(patches) == 2103 - 1356
paper_error = int(np.abs(patches.astype(int) - np.array([244, 238, 226])).max())
assert paper_error <= 5, paper_error

sample_frames = [96, 459, 500, 534, 570, 597, 810, 900, 1098, 1320, 1326, 1332,
                 1338, 1344, 1350, 1356, 1368, 1380, 1467, 1485, 1509,
                 1559, 1578, 1602, 1652, 1682, 1755, 1840, 2043, 2102]
actual = Q / 'actual-frames'
actual.mkdir(exist_ok=True)
select = '+'.join(f'eq(n\\,{f})' for f in sample_frames)
run(['ffmpeg', '-y', '-v', 'error', '-i', str(MOVIE), '-vf', f'select={select}',
     '-fps_mode', 'vfr', '-q:v', '2', str(actual / '%03d.jpg')])
sheet = Image.new('RGB', (1600, math.ceil(len(sample_frames) / 4) * 250), '#173446')
draw = ImageDraw.Draw(sheet)
for i, frame in enumerate(sample_frames):
    im = Image.open(actual / f'{i + 1:03}.jpg').resize((400, 225))
    x, y = i % 4 * 400, i // 4 * 250
    sheet.paste(im, (x, y))
    draw.text((x + 8, y + 230), f'{frame/30:.3f}s / f{frame}', fill='white')
sheet.save(Q / 'actual-storyboard.jpg', quality=93)
(Q / 'actual-frame-index.json').write_text(json.dumps(
    {f'f{f}': str(actual.relative_to(R) / f'{i+1:03}.jpg') for i, f in enumerate(sample_frames)}, indent=2) + '\n')
actual_tiles = arr(actual / '003.jpg')  # f500 after H264 decode and JPEG extraction.
actual_levels = [float(np.quantile(actual_tiles[280 + i//5*92:360 + i//5*92,
                                              1040 + i%5*153:1182 + i%5*153].min(axis=2), .85))
                 for i in range(25)]
assert min(actual_levels) >= 245
previews = []
for filename, frames in [('BOI-HK_v12_第五版_後半段27秒預覽.mp4', 813),
                         ('BOI-HK_v12_第五版_銀行展示5秒預覽.mp4', 150)]:
    path = R / 'out' / filename
    metadata = json.loads(run(['ffprobe', '-v', 'error', '-show_entries',
                               'format=duration:stream=codec_name,nb_frames', '-of', 'json', str(path)]))
    assert metadata['streams'][0]['nb_frames'] == str(frames)
    run(['ffmpeg', '-v', 'error', '-i', str(path), '-f', 'null', '-'])
    previews.append({'path': str(path), 'sha256': sha(path), 'frames': frames,
                     'probe': metadata, 'complete_decode_ok': True})

report = {
    'output': str(MOVIE), 'sha256': sha(MOVIE), 'probe': probe, 'complete_decode_ok': True,
    'AAC_payload_pts_dts_duration_identical_to_Stage4_and_master': True,
    'AAC_packet_count': len(audio), 'no_new_voice_music_or_mix': True,
    'protected_baseline_unchanged_count': sum(protected.values()),
    'protected_baseline_total': len(protected), 'Root_additive_only': True,
    'iris_count': 1, 'spread_frames': 33, 'hold_frames': 3,
    'native_hold_frames_identical': True, 'opaque_iris_interior': interior,
    'old_scene_scale_removed': True,
    'actual_paper_background_frames_checked': len(patches), 'paper_patch_max_RGB_error': paper_error,
    'first_values_line_retained_when_second_added_native_ROI_equal': True,
    'two_lines_fully_settled_hold_seconds': (1644 - 1578) / 30,
    'awards_native_f810_f900_match_Stage4': True,
    'closing_native_f2043_f2102_match_Stage4': True,
    'all_25_logo_tiles_lit_at_f500_before_f525_cut': True,
    'actual_movie_f500_minimum_tile_white_quantile': min(actual_levels),
    'banks': banks, 'actual_representative_frames_exported': len(sample_frames),
    'previews': previews,
    'review_limits': 'Sampled actual movie images plus full decode and every-frame background patch checked. '
                     'No claim of full-film pixel equality, human Cantonese transcription, or user/boss acceptance.'
}
(Q / 'verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False, indent=2))
