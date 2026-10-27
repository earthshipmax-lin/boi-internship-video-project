"""Replace only v6 logo bookends; copy the six approved body video streams.
All seven voice segments use the same prepared PCM as v6, with no new atempo.
Run render-logo-bookends-v7.mjs before this script. Existing movies are retained.
"""
from pathlib import Path
import json,subprocess,wave,hashlib
ROOT=Path(__file__).resolve().parents[1]
Q=ROOT/'qa/v7';PARTS=Q/'parts';V6=ROOT/'qa/v6/parts'
OUTPUT=ROOT/'out/BOI-HK_MiniMax粵語_首尾Logo動效_v7.mp4'
timing=json.loads((ROOT/'src/config/logo-hk-v7.json').read_text())
if OUTPUT.exists():raise FileExistsError(f'Refusing to overwrite {OUTPUT}')
for name in ('intro','outro'):
 target=PARTS/f'{name}.mp4'
 subprocess.run(['ffmpeg','-v','error','-nostdin','-n','-i',str(PARTS/f'{name}-native.mp4'),
  '-an','-vf','scale=in_range=tv:out_range=pc:out_color_matrix=bt601,format=yuvj420p',
  '-c:v','libx264','-preset','slow','-crf','14','-profile:v','high','-level:v','5.0',
  '-color_range','pc','-colorspace','bt470bg','-video_track_timescale','15360',str(target)],check=True)
with wave.open(str(V6/'S1.wav'),'rb')as w:params=w.getparams()
with wave.open(str(PARTS/'intro.wav'),'wb')as w:
 w.setparams(params)
 w.writeframes(b'\0'*(timing['introFrames']*1600*params.nchannels*params.sampwidth))
videos=[PARTS/'intro.mp4']+[V6/f'S{i}.mp4'for i in range(1,7)]+[PARTS/'outro.mp4']
audio=[PARTS/'intro.wav']+[V6/f'S{i}.wav'for i in range(1,8)]
for filename,files in [('video-list.txt',videos),('audio-list.txt',audio)]:
 (PARTS/filename).write_text(''.join("file '"+str(p).replace("'","'\\''")+"'\n"for p in files))
with wave.open(str(Q/'expected-audio.wav'),'wb')as out:
 out.setparams(params)
 for p in audio:
  with wave.open(str(p),'rb')as w:
   assert w.getnchannels()==params.nchannels and w.getframerate()==48000
   out.writeframes(w.readframes(w.getnframes()))
subprocess.run(['ffmpeg','-v','error','-nostdin','-n','-f','concat','-safe','0','-i',str(PARTS/'video-list.txt'),
 '-i',str(Q/'expected-audio.wav'),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','256k','-ar','48000',
 '-video_track_timescale','15360','-movflags','+faststart',str(OUTPUT)],check=True)
report={'file':str(OUTPUT),'frames':timing['frames'],'seconds':timing['frames']/30,
 'bodyCopiedFrom':list(map(str,videos[1:-1])),'audioSource':'v6 PCM segments, without another speed or pitch operation',
 'sha256':hashlib.sha256(OUTPUT.read_bytes()).hexdigest()}
(Q/'assembly.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
