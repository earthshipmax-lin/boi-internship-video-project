from pathlib import Path
import json,subprocess,hashlib,wave,shutil,math
import torch,whisper
from whisper.timing import find_alignment
from whisper.tokenizer import get_tokenizer
R=Path(__file__).resolve().parents[1];q=R/'qa/us-v1-60s-v2';out=R/'public/vo/us-v2';profile=json.loads((R/'src/config/performance-us-v2.json').read_text());old=json.loads((R/'src/config/us-full-timeline.json').read_text());torch.set_num_threads(4);model=whisper.load_model('tiny',device='cpu',download_root=str(R/'.model-cache'));tok=get_tokenizer(multilingual=model.is_multilingual,num_languages=model.num_languages,language='en',task='transcribe');records=[]
reused={'S0':'S0','S2':'S2','S7':'S6'}
for id in ['S0','S1','S2','S3','S4','S5','S6','S7']:
 target=out/f'{id}.wav'
 if id in reused:
  prev=next(s for s in old['scenes'] if s['id']==reused[id]);shutil.copy2(R/'public'/prev['source'],target);rec={**prev,'id':id,'source':f'vo/us-v2/{id}.wav','reused':True,'reuseFrom':prev['source']};records.append(rec);continue
 c=profile['scenes'][id];source=q/f'source/{id}.mp3';subprocess.run(['ffmpeg','-v','error','-y','-i',str(source),'-ar','48000','-ac','1','-c:a','pcm_s16le',str(target)],check=True)
 with wave.open(str(target),'rb') as w:dur=w.getnframes()/w.getframerate()
 audio=whisper.load_audio(str(target));nf=len(audio)//whisper.audio.HOP_LENGTH;mel=whisper.log_mel_spectrogram(whisper.pad_or_trim(audio),n_mels=model.dims.n_mels);words=find_alignment(model,tok,tok.encode(c['text']),mel,nf);wr=[{'word':w.word,'start':float(w.start),'end':float(w.end)} for w in words];asr=model.transcribe(str(target),language='en',fp16=False,verbose=None)['text'];(q/f'{id}-alignment.json').write_text(json.dumps({'referenceWords':wr,'independentASR':asr},indent=2));records.append({'id':id,'duration':dur,'source':f'vo/us-v2/{id}.wav','playbackRate':1,'text':c['text'],'synthesisText':c['synthesisText'],'words':wr,'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'reused':False});print(id,dur,asr,flush=True)
# Priorities: original4s opener,8s team, completeunsped speech, thirdscale-row1s still, closinglogo≥1.5s still.
offsets=[6,6,24,6,6,6,6,3];minimum=[]
for i,r in enumerate(records):
 n=math.ceil(r['duration']*30)+offsets[i]+9
 if i==0:n=120
 if i==2:n=240
 if i==3:
  cue=next(w for w in r['words'] if w['word'].strip().lower()=='three')['start'];n=max(n,offsets[i]+math.ceil(cue*30)+20+30+9)
 if i==4:
  cue=next(w for w in r['words'] if 'century' in w['word'].lower())['start'];n=max(n,offsets[i]+math.ceil(cue*30)+18+20+9)
 if i==6:n=max(n,90)
 if i==7:n=max(n,210)
 minimum.append(n)
base=[120,240,240,270,270,360,130,230];target=max(1800,sum(minimum));assert target<=1860,(minimum,target)
lengths=minimum[:];extra=target-sum(lengths)
# Restore generous intended holds first, retaining allfixed1800ifvoice permits.
for i in [1,5,3,4,6,7]:
 take=min(extra,max(0,base[i]-lengths[i]));lengths[i]+=take;extra-=take
lengths[7]+=extra
cursor=0
for r,n,offset in zip(records,lengths,offsets):r.update(startFrame=cursor,endFrame=cursor+n,voiceStartFrame=cursor+offset);cursor+=n;assert r['voiceStartFrame']/30+r['duration']<=cursor/30
T={'fps':30,'duration':target/30,'frames':target,'scenes':records};(R/'src/config/us-full-v2-timeline.json').write_text(json.dumps(T,indent=2));(q/'timeline.json').write_text(json.dumps(T,indent=2));credits=json.loads((q/'credits.json').read_text());prov={'provider':'MiniMaxwebsite','model':profile['model'],'voice':profile['voiceDisplayName'],'language':'English-detected/nativeUSvoice','speed':1,'pitch':0,'volume':1,'playbackRate':1,'segments':records,'creditsByScene':credits,'timing':'Whisper tiny English reference-text alignment; independent ASR; no human certifiederror'};(out/'VOICE_PROVENANCE.json').write_text(json.dumps(prov,indent=2));(q/'VOICE_PROVENANCE.json').write_text(json.dumps(prov,indent=2));print('TIMELINE',[(r['id'],r['startFrame'],r['endFrame']) for r in records],target/30)
