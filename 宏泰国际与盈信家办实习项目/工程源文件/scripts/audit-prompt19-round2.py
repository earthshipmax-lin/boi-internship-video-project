from pathlib import Path
import json,subprocess
import numpy as np
import torch,whisper
from whisper.timing import find_alignment
from whisper.tokenizer import get_tokenizer
V=Path(__file__).resolve().parents[1];Q=V/'qa/v19/round2';torch.set_num_threads(4);m=whisper.load_model('small',device='cpu',download_root=str(V/'.model-cache'));tok=get_tokenizer(multilingual=True,num_languages=m.num_languages,language='zh',task='transcribe');rows=[];cache={r["id"]:r for r in json.loads((Q/"source-audit.json").read_text())} if (Q/"source-audit.json").exists() else {}
for record in json.loads((Q/'generation-log.json').read_text()):
 if record['id'] in cache:
  rows.append(cache[record['id']]);continue
 p=V/record['file'];audio=whisper.load_audio(str(p));expected='稳如泰山。' if record['id'].startswith('line2') else '宏泰，国际。';mel=whisper.log_mel_spectrogram(whisper.pad_or_trim(audio),n_mels=m.dims.n_mels);alignment=find_alignment(m,tok,tok.encode(expected),mel,len(audio)//whisper.audio.HOP_LENGTH)
 asr=m.transcribe(str(p),language='zh',fp16=False,verbose=None);a=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-ar','48000','-ac','1','-f','f32le','-']),dtype='<f4');env=np.array([np.max(np.abs(a[i:i+480])) for i in range(0,len(a),480)]);active=np.where(env>10**(-43/20))[0];quiet=[];start=None
 for i,v in enumerate(env):
  if v<=10**(-43/20) and start is None:start=i
  if (v>10**(-43/20) or i==len(env)-1) and start is not None:
   if i-start>=8:quiet.append([start*.01,i*.01,(i-start)*.01])
   start=None
 row={**record,'seconds':len(a)/48000,'independentASR':asr['text'],'words':[{'word':x.word,'start':float(x.start),'end':float(x.end)} for x in alignment],'speechBoundsSeconds':[active[0]*.01,(active[-1]+1)*.01],'quietRuns':quiet};rows.append(row);print(record['id'],asr['text'],row['words'],quiet,flush=True)
(Q/'source-audit.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
