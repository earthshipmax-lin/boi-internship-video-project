from pathlib import Path
import json
import torch,whisper
from whisper.timing import find_alignment
from whisper.tokenizer import get_tokenizer
V=Path(__file__).resolve().parents[1];Q=V/'qa/v16';torch.set_num_threads(4);m=whisper.load_model('small',device='cpu',download_root=str(V/'.model-cache'));p=V/'public/vo/hk-v16/cn/ending-emotion-r02.wav';a=whisper.load_audio(str(p));mel=whisper.log_mel_spectrogram(whisper.pad_or_trim(a),n_mels=m.dims.n_mels);tok=get_tokenizer(multilingual=True,num_languages=m.num_languages,language='zh',task='transcribe');w=find_alignment(m,tok,tok.encode('大展宏图，稳如泰山。宏泰国际！'),mel,len(a)//whisper.audio.HOP_LENGTH);asr=m.transcribe(str(p),language='zh',fp16=False,verbose=None)
r={'source':str(p.relative_to(V)),'seconds':len(a)/16000,'expected':'大展宏图，稳如泰山。宏泰国际！','independentASR':asr['text'],'words':[{'word':t.word,'start':float(t.start),'end':float(t.end)} for t in w],'voice':'BOI-HK-v13-R06-Clone-r01','model':'MiniMax speech-2.8-hd','speed':.88,'pitch':1,'volume':1,'pauseTags':[.35,.5,.2],'emotion':'happy on all four text spans','creditsBefore':6604,'creditsAfter':6549,'credits':55,'limits':'ASR and alignment are diagnostic; vocal emotion remains subject to user listening.'}
(Q/'cn-ending-alignment.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps(r,ensure_ascii=False))
