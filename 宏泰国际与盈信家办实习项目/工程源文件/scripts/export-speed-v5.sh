#!/bin/sh
# Speed-only derivative. Existing output is never overwritten; v4 stays untouched.
set -eu
cd "$(dirname "$0")/.."
ffmpeg -hide_banner -loglevel error -nostdin -n \
 -i 'out/BOI-HK_MiniMax粵語_中英Logo_v4.mp4' \
 -filter_complex '[0:v]setpts=(PTS-STARTPTS)*590/751,fps=30[v];[0:a]atempo=1.2728813559322034,apad=whole_dur=59,atrim=duration=59[a]' \
 -map '[v]' -map '[a]' -c:v libx264 -preset slow -crf 14 -pix_fmt yuv420p \
 -c:a aac -b:a 256k -ar 48000 -movflags +faststart \
 'out/BOI-HK_MiniMax粵語_59秒加速_v5.mp4'
