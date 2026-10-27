"""Local independent ASR and reference alignment; diagnostic, not a listening approval."""
from pathlib import Path
import json,hashlib
import torch,whisper
from whisper.timing import find_alignment
from whisper.tokenizer import get_tokenizer
V=Path(__file__).resolve().parents[1];Q=V/'qa/v13/full/final-r01/speech-audit';Q.mkdir(parents=True,exist_ok=True)
torch.set_num_threads(4);model=whisper.load_model('tiny',device='cpu',download_root=str(V/'.model-cache'))
rows=json.loads((V/'qa/v13/people/voice-production-r01/downloads.json').read_text())
for row in rows:
 source=(V/row['output']).with_suffix('.wav');out=Q/f"{row['locale']}-{row['id']}.json"
 if out.exists():continue
 if not source.exists():continue
 lang='en' if row['locale']=='en' else 'zh';tok=get_tokenizer(multilingual=True,num_languages=model.num_languages,language=lang,task='transcribe')
 a=whisper.load_audio(str(source));mel=whisper.log_mel_spectrogram(whisper.pad_or_trim(a),n_mels=model.dims.n_mels)
 words=find_alignment(model,tok,tok.encode(row['text']),mel,len(a)//whisper.audio.HOP_LENGTH)
 recognized=model.transcribe(str(source),language=lang,fp16=False,verbose=None)['text']
 data={'source':str(source.relative_to(V)),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'expected':row['text'],'independentASR':recognized,'referenceWords':[{'word':w.word,'start':float(w.start),'end':float(w.end)} for w in words],'model':'local Whisper tiny','limitation':'ASR and forced alignment are diagnostic evidence only; short multilingual speech may be misrecognized. Not a perceptual voice or pronunciation approval.'}
 out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print(row['locale'],row['id'],recognized,flush=True)
