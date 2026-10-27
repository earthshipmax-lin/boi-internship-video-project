from pathlib import Path
import json,subprocess,hashlib,wave,shutil
import torch,whisper
from whisper.timing import find_alignment
from whisper.tokenizer import get_tokenizer
R=Path(__file__).resolve().parents[1];q=R/'qa/us-v1-60s';out=R/'public/vo/us-v1/full';profile=json.loads((R/'src/config/performance-us-v1.json').read_text());torch.set_num_threads(4);model=whisper.load_model('tiny',device='cpu',download_root=str(R/'.model-cache'));tok=get_tokenizer(multilingual=model.is_multilingual,num_languages=model.num_languages,language='en',task='transcribe')
records=[]
credits={'S0':[2913,2862],'S1':[2862,None],'S2':[None,None]}
for i,(id,c) in enumerate(profile['fullFilmScenes'].items()):
 target=out/f'{id}.wav'
 if id=='S2':shutil.copy2(R/'public/vo/us-v1/team-b/VO-01.wav',target);source=R/'qa/us-v1-voice-b/team-b-source.mp3'
 else:
  source=q/f'source/{id}.mp3';subprocess.run(['ffmpeg','-v','error','-y','-i',str(source),'-ar','48000','-ac','1','-c:a','pcm_s16le',str(target)],check=True)
 with wave.open(str(target),'rb') as w:dur=w.getnframes()/w.getframerate()
 audio=whisper.load_audio(str(target));nf=len(audio)//whisper.audio.HOP_LENGTH;mel=whisper.log_mel_spectrogram(whisper.pad_or_trim(audio),n_mels=model.dims.n_mels);words=find_alignment(model,tok,tok.encode(c['text']),mel,nf);wr=[{'word':w.word,'start':float(w.start),'end':float(w.end)} for w in words]
 asr=model.transcribe(str(target),language='en',fp16=False,verbose=None)['text'];(q/f'{id}-alignment.json').write_text(json.dumps({'referenceWords':wr,'independentASR':asr},indent=2))
 records.append({'id':id,'duration':dur,'source':f'vo/us-v1/full/{id}.wav','playbackRate':1,'text':c['text'],'synthesisText':c['synthesisText'],'words':wr,'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'reused':id=='S2'})
 print(id,dur,asr,flush=True)
# Keep8s team, preserve original design targets; borrow excess from generous12s timeline/11s closing.
lens=[120,210,240,360,300,240,330]
for i,r in enumerate(records):
 minimum=round((r['duration']+(.4 if i==0 else .85))*30)
 if i==2:assert minimum<=240
 elif minimum>lens[i]:
  excess=minimum-lens[i];lens[i]=minimum
  for donor in [3,6,4]:
   spare=max(0,lens[donor]-round((records[donor]['duration']+1.2)*30));take=min(excess,spare);lens[donor]-=take;excess-=take
   if not excess:break
  assert not excess,'Speech does not fit60s without rewriting'
assert sum(lens)==1800
cursor=0
for r,n in zip(records,lens):r.update(startFrame=cursor,endFrame=cursor+n,voiceStartFrame=cursor+(6 if r['id']=='S0' else 24));cursor+=n;assert r['voiceStartFrame']/30+r['duration']<=cursor/30
T={'fps':30,'duration':60,'frames':1800,'scenes':records};(R/'src/config/us-full-timeline.json').write_text(json.dumps(T,indent=2));(q/'timeline.json').write_text(json.dumps(T,indent=2));(out/'VOICE_PROVENANCE.json').write_text(json.dumps({'provider':'MiniMax website','model':'speech-2.8-hd','voice':profile['voiceDisplayName'],'language':'English - detected / native US voice','speed':1,'pitch':0,'volume':1,'playbackRate':1,'records':records,'credits':'See qa/us-v1-60s/credits.json','timingMethod':'Whisper tiny English reference-text alignment, approximate; independent ASR recorded'},indent=2))
