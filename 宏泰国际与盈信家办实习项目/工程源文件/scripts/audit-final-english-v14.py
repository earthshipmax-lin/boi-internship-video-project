from pathlib import Path
import json,re,difflib
import torch,whisper
V=Path(__file__).resolve().parents[1];Q=V/'qa/v14';torch.set_num_threads(4);model=whisper.load_model('small',device='cpu',download_root=str(V/'.model-cache'))
r=model.transcribe(str(V/'public/music/hk-v14/en-voice.wav'),language='en',fp16=False,verbose=None,condition_on_previous_text=False)
def norm(s):
 s=s.lower().replace('1.5','one point five').replace('20,000','twenty thousand').replace('20000','twenty thousand').replace('1997','nineteen ninety seven');s=re.sub(r'\b10\b','ten',s);s=re.sub(r'\b30\b','thirty',s);return re.findall(r"[a-z]+(?:'[a-z]+)?",s)
expected=' '.join(c['text'] for c in json.loads((Q/'english-narration.json').read_text()));a=norm(expected);b=norm(r['text']);matcher=difflib.SequenceMatcher(a=a,b=b,autojunk=False)
out={'expected':expected,'transcript':r['text'],'normalizedRatio':matcher.ratio(),'differences':[(o,a[i:j],b[k:l]) for o,i,j,k,l in matcher.get_opcodes() if o!='equal'],'model':'Whisper small','source':'public/music/hk-v14/en-voice.wav','limits':'Independent transcription checks word content; no human pronunciation or audience approval claimed.'}
(Q/'english-final-voice-check.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out['differences']));print(out['normalizedRatio'])
