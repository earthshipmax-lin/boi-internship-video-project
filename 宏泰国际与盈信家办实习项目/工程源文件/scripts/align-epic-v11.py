from pathlib import Path
import json,re,unicodedata
import torch,whisper
from whisper.timing import find_alignment
from whisper.tokenizer import get_tokenizer
ROOT=Path(__file__).resolve().parents[1];q=ROOT/'qa/v11/film'
def norm(s):return ''.join(c for c in s if unicodedata.category(c)[0] in 'LN')
text=(ROOT/'qa/v11/voice-r06/script.txt').read_text();cut=text.index('深圳')+2
chunks=[(0,29.94,text[:cut]),(29.94,59.956644,text[cut:])]
torch.set_num_threads(4);m=whisper.load_model('tiny',device='cpu',download_root=str(ROOT/'.model-cache'));tok=get_tokenizer(multilingual=True,num_languages=m.num_languages,language='zh',task='transcribe')
a=whisper.load_audio(str(ROOT/'public/vo/hk-v11/full-r06.mp3'));chars=[]
for start,end,ref in chunks:
 audio=a[round(start*16000):round(end*16000)];frames=min(len(audio)//160,3000)
 mel=whisper.log_mel_spectrogram(whisper.pad_or_trim(audio),n_mels=m.dims.n_mels)
 words=find_alignment(m,tok,tok.encode(ref),mel,frames)
 for w in words:
  word=norm(w.word)
  for i,ch in enumerate(word):
   chars.append({'char':ch,'start':start+w.start+(w.end-w.start)*i/max(1,len(word)),'end':start+w.start+(w.end-w.start)*(i+1)/max(1,len(word))})
assert ''.join(c['char'] for c in chars)==norm(text)
texts=['一個家族嘅未來','值得我哋睇得更遠','源自一九九七年','我哋一路走來，靠嘅係專業','更加係每一份交到手上嘅信任','集團總保費超過一百億港元','總佣金超過十五億港元','服務超過兩萬位高淨值客戶','每一個數字背後','都有一個家庭，對未來嘅期望','所以，我哋一直向前','連繫香港、深圳、紐約','新加坡亦正籌備中','從保險、信託，到稅務','教育同身份規劃','將專業連成一個平台','為每一個家族','睇得更全面，行得更長遠','眼光，可以跨越地域','信任，需要時間扎根','根扎得深，先可以長得更高','步伐夠穩，先可以走得更遠','大展宏圖，穩如泰山','宏泰國際']
assert norm(''.join(texts))==norm(text)
pos=0;caps=[];offset=2.4
for phrase in texts:
 n=len(norm(phrase));start=chars[pos]['start'];end=chars[pos+n-1]['end'];pos+=n
 caps.append({'text':phrase,'start':round(start+offset,3),'end':round(max(start+.25,end)+offset,3)})
 # Small source-alignment uncertainties are retained, not claimed as independent transcription.
(ROOT/'src/config/captions-v11.json').write_text(json.dumps(caps,ensure_ascii=False,indent=2)+'\n')
(q/'forced-alignment.json').write_text(json.dumps({'voice_offset_s':offset,'method':'local Whisper tiny reference-text forced alignment in two windows, boundary informed by ASR; not independent Cantonese verification','characters':chars,'captions':caps},ensure_ascii=False,indent=2)+'\n')
for c in caps:print(c)
