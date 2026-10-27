"""Verify decoded video frames and uncompressed audio samples across a scoped revision.

Only reads local input media; no account access or network requests. Video comparisons
apply only to the requested prefix. Lossy audio exports must not be represented as
sample-exact; use the source PCM masters for an exact audio comparison.
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path


def video_hashes(path, frames):
    data = subprocess.check_output([
        'ffmpeg', '-v', 'error', '-i', str(path), '-map', '0:v:0',
        '-frames:v', str(frames), '-f', 'framemd5', '-'
    ]).decode()
    return [line.rsplit(',', 1)[-1].strip() for line in data.splitlines()
            if line and not line.startswith('#')]


def audio_prefix(path, samples, rate, channels):
    return subprocess.check_output([
        'ffmpeg', '-v', 'error', '-i', str(path), '-map', '0:a:0',
        '-af', f'aresample={rate},atrim=end_sample={samples}', '-ar', str(rate),
        '-ac', str(channels), '-f', 'f32le', '-'
    ])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('reference', type=Path)
    parser.add_argument('candidate', type=Path)
    parser.add_argument('--frames', type=int)
    parser.add_argument('--samples', type=int)
    parser.add_argument('--rate', type=int, default=48000)
    parser.add_argument('--channels', type=int, default=2)
    args = parser.parse_args()
    if (args.frames is None) == (args.samples is None):
        parser.error('Choose exactly one of --frames or --samples.')
    if min(args.frames or 1, args.samples or 1, args.rate, args.channels) < 1:
        parser.error('All counts must be positive.')
    if args.frames:
        before = video_hashes(args.reference, args.frames)
        after = video_hashes(args.candidate, args.frames)
        passed = len(before) == len(after) == args.frames and before == after
        report = {'mode': 'decoded_video_prefix', 'requestedFrames': args.frames,
                  'referenceFrames': len(before), 'candidateFrames': len(after)}
    else:
        before = audio_prefix(args.reference, args.samples, args.rate, args.channels)
        after = audio_prefix(args.candidate, args.samples, args.rate, args.channels)
        expected = args.samples * args.channels * 4
        passed = len(before) == len(after) == expected and before == after
        report = {'mode': 'decoded_float32_audio_prefix', 'requestedSamples': args.samples,
                  'sampleRate': args.rate, 'channels': args.channels,
                  'referenceBytes': len(before), 'candidateBytes': len(after),
                  'referenceSHA256': hashlib.sha256(before).hexdigest(),
                  'candidateSHA256': hashlib.sha256(after).hexdigest()}
    report['equal'] = passed
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if passed else 1)


if __name__ == '__main__':
    main()
