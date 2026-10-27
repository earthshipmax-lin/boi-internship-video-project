"""Local-only, gain-only audition normalization and manifest verification.

Inputs, private metadata and output media are supplied locally and are not
part of this source repository. Requires ffmpeg, ffprobe and numpy.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import numpy as np


def run(args):
    return subprocess.check_output(args)


def loudness(path):
    result = subprocess.run(
        ['ffmpeg', '-hide_banner', '-i', str(path), '-af',
         'aformat=channel_layouts=stereo,loudnorm=I=-16:TP=-1:LRA=11:print_format=json',
         '-f', 'null', '-'], capture_output=True, text=True, check=True)
    return json.loads(re.findall(r'\{\s*"input_i".*?\}', result.stderr, re.S)[-1])


def pcm(path):
    return np.frombuffer(run(['ffmpeg', '-v', 'error', '-i', str(path),
                              '-ar', '48000', '-ac', '2', '-f', 'f32le', '-']),
                         dtype='<f4').astype(np.float64)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize(source, output, target, ceiling):
    if output.exists():
        raise FileExistsError('Refusing to overwrite an existing audition')
    measured = loudness(source)
    gain = target - float(measured['input_i'])
    if float(measured['input_tp']) + gain > ceiling:
        raise ValueError('Static gain cannot meet both loudness and peak targets')
    subprocess.run(['ffmpeg', '-v', 'error', '-n', '-i', str(source), '-af',
                    f'aformat=channel_layouts=stereo,volume={gain}dB',
                    '-ar', '48000', '-ac', '2', '-c:a', 'pcm_s24le', str(output)], check=True)
    final = loudness(output)
    assert abs(float(final['input_i']) - target) <= .5
    assert float(final['input_tp']) <= ceiling
    return {'loudnessLUFS': float(final['input_i']),
            'truePeakDBTP': float(final['input_tp']), 'gainDB': gain}


def verify(manifest, root, protected):
    data = json.loads(manifest.read_text())
    rows = {}
    for name, take in data['takes'].items():
        source, output = root / take['source'], root / take['file']
        assert digest(source) == take['sourceSHA256']
        assert digest(output) == take['sha256']
        a, b = pcm(source), pcm(output)
        assert len(a) == len(b)
        gain = float(np.dot(a, b) / np.dot(a, a))
        error = float(np.max(np.abs(b - a * gain)))
        assert error < 2e-6, 'Output differs from gain-only processing'
        assert take['ASRAcceptedExactOrAllowedHomophone']
        measured = loudness(output)
        assert abs(float(measured['input_i']) + 16) <= .5
        assert float(measured['input_tp']) <= -1
        rows[name] = {'sameSampleCount': True, 'gainOnlyMaxError': error}
    count = 0
    if protected:
        baseline = json.loads(protected.read_text())
        assert all((root / p).is_file() and digest(root / p) == h
                   for p, h in baseline.items()), 'Protected file changed'
        count = len(baseline)
    return {'auditions': rows, 'protectedFilesUnchanged': count}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='command', required=True)
    normal = sub.add_parser('normalize')
    normal.add_argument('source', type=Path)
    normal.add_argument('output', type=Path)
    normal.add_argument('--lufs', type=float, default=-16)
    normal.add_argument('--peak', type=float, default=-1)
    check = sub.add_parser('verify')
    check.add_argument('manifest', type=Path)
    check.add_argument('--root', type=Path, default=Path('.'))
    check.add_argument('--protected', type=Path)
    args = parser.parse_args()
    result = (normalize(args.source, args.output, args.lufs, args.peak)
              if args.command == 'normalize'
              else verify(args.manifest, args.root, args.protected))
    print(json.dumps(result, indent=2))
