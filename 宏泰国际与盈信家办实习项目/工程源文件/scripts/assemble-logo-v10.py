"""Replace only the brand artwork in bookends; copy all six approved body video streams.
Copy the complete v9 AAC track without decoding, mixing or re-encoding.
Run render-logo-bookends-v10.mjs before this script. Existing movies are retained.
"""
from pathlib import Path
import json,subprocess,wave,hashlib
ROOT=Path(__file__).resolve().parents[1]
Q=ROOT/'qa/v10';PARTS=Q/'parts';V6=ROOT/'qa/v6/parts'
OUTPUT=ROOT/'out/BOI-HK_MiniMax粵語_原版SVG標誌_v10.mp4'
timing=json.loads((ROOT/'src/config/logo-hk-v7.json').read_text())
if OUTPUT.exists():raise FileExistsError(f'Refusing to overwrite {OUTPUT}')
for name in ('intro','outro'):
 target=PARTS/f'{name}.mp4'
 subprocess.run(['ffmpeg','-v','error','-nostdin','-n','-i',str(PARTS/f'{name}-native.mp4'),
  '-an','-vf','scale=in_range=tv:out_range=pc:out_color_matrix=bt601,format=yuvj420p',
  '-c:v','libx264','-preset','slow','-crf','14','-profile:v','high','-level:v','5.0',
  '-color_range','pc','-colorspace','bt470bg','-video_track_timescale','15360',str(target)],check=True)
videos=[PARTS/'intro.mp4']+[V6/f'S{i}.mp4'for i in range(1,7)]+[PARTS/'outro.mp4']
(PARTS/'video-list.txt').write_text(''.join("file '"+str(p).replace("'","'\\''")+"'\n"for p in videos))
AUDIO=ROOT/'out/BOI-HK_MiniMax粵語_物件音效與柔和年輪_v9.mp4'
subprocess.run(['ffmpeg','-v','error','-nostdin','-n','-f','concat','-safe','0','-i',str(PARTS/'video-list.txt'),
 '-i',str(AUDIO),'-map','0:v','-map','1:a:0','-c','copy',
 '-video_track_timescale','15360','-movflags','+faststart',str(OUTPUT)],check=True)
report={'file':str(OUTPUT),'frames':timing['frames'],'seconds':timing['frames']/30,
 'bodyCopiedFrom':list(map(str,videos[1:-1])),'audioSource':'v9 AAC bitstream copied without re-encoding; all narration and SFX unchanged',
 'sha256':hashlib.sha256(OUTPUT.read_bytes()).hexdigest()}
(Q/'assembly.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
