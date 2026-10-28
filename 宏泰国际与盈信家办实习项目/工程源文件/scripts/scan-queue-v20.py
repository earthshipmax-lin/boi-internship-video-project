from pathlib import Path
import time,subprocess
V=Path(__file__).resolve().parents[1];Q=V/'qa/v20'
for loc,nextloc in [('yue','en'),('en',None)]:
 while True:
  text=(Q/'render.log').read_text()
  if f'{loc} 100%' in text and (nextloc is None or f'{nextloc} 0%' in text):break
  time.sleep(5)
 # Rendering 100% precedes file close; ffprobe confirms complete mux.
 time.sleep(3)
 with (Q/f'{loc}-ocr.log').open('w') as log:subprocess.run([str(Q/'scan-v20'),str(Q/f'{loc}-picture.mp4'),str(Q/f'{loc}-ocr.jsonl'),str(Q/f'{loc}-ocr-summary.json')],stdout=log,stderr=log,check=True)
