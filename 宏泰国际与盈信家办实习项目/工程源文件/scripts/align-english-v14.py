from pathlib import Path
import json,re,difflib
import torch,whisper
V=Path(__file__).resolve().parents[1];Q=V/'qa/v14';torch.set_num_threads(6)
model=whisper.load_model('small',device='cpu',download_root=str(V/'.model-cache'))
raw=model.transcribe(str(V/'public/vo/hk-v14/en/full-source.wav'),language='en',fp16=False,word_timestamps=True,verbose=None,condition_on_previous_text=False)
(Q/'english-independent-asr.json').write_text(json.dumps(raw,ensure_ascii=False,indent=2))
def words(s):
 s=s.lower().replace('1.5','one point five').replace('20,000','twenty thousand').replace('20000','twenty thousand').replace('1997','nineteen ninety seven')
 s=re.sub(r'\b10\b','ten',s)
 return re.findall(r"[a-z]+(?:'[a-z]+)?",s)
asr=[]
for seg in raw['segments']:
 for w in seg.get('words',[]):
  for tok in words(w['word']):asr.append({'token':tok,'start':w['start'],'end':w['end']})
expected=json.loads((Q/'english-narration.json').read_text());tokens=[];spans=[]
for row in expected:
 first=len(tokens);tokens+=words(row['text']);spans.append((first,len(tokens)))
matcher=difflib.SequenceMatcher(a=tokens,b=[w['token'] for w in asr],autojunk=False);mapping={}
for b in matcher.get_matching_blocks():
 for i in range(b.size):mapping[b.a+i]=b.b+i
out=[]
for row,(a,b) in zip(expected,spans):
 hits=[mapping[i] for i in range(a,b) if i in mapping];assert hits,row
 first=min(hits);last=max(hits)
 out.append({**row,'start':asr[first]['start'],'end':asr[last]['end'],'matchedTokens':len(hits),'expectedTokens':b-a,'recognized':' '.join(w['token'] for w in asr[first:last+1])})
(Q/'english-alignment.json').write_text(json.dumps({'ratio':matcher.ratio(),'cues':out,'source':'public/vo/hk-v14/en/full-source.wav','method':'independent Whisper small word alignment; exact script matched monotonically','limits':'ASR is diagnostic, not human pronunciation approval'},ensure_ascii=False,indent=2))
print(json.dumps({'ratio':matcher.ratio(),'cues':len(out),'end':out[-1]['end']},ensure_ascii=False))
