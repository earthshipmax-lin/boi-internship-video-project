"""Independent diagnostic for the two selected numeric retakes."""
from pathlib import Path
import json, hashlib
import torch, whisper

V=Path(__file__).resolve().parents[1]
torch.set_num_threads(4)
m=whisper.load_model('base',device='cpu',download_root=str(V/'.model-cache'))
rows=[]
for folder,id,lang,expected in [('en','caption-07-r02','en','one point five billion Hong Kong dollars'),('cn','caption-06-r02','zh','一百亿港元')]:
 p=V/f'public/vo/hk-v13/{folder}/{id}.wav'
 text=m.transcribe(str(p),language=lang,fp16=False,verbose=None)['text']
 rows.append({'file':str(p.relative_to(V)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'expectedNumber':expected,'independentASR':text})
 print(folder,id,text,flush=True)
(V/'qa/v13/full/final-r01/number-retakes-asr.json').write_text(json.dumps({'model':'local Whisper base','records':rows,'limit':'Independent speech recognition is diagnostic, not full human listening approval.'},ensure_ascii=False,indent=2)+'\n')
