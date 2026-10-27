"""US adaptation of prepare-minimax-v4.py: browser originals only, isolated US outputs.
This pilot prepares auditions; final narration stays unset until user voice selection.
"""
from pathlib import Path
import json,subprocess,hashlib,unicodedata,wave
import torch,whisper
from whisper.timing import find_alignment
from whisper.tokenizer import get_tokenizer
ROOT=Path(__file__).resolve().parents[1];q=ROOT/'qa/us-v1';src=q/'voice-auditions';out=ROOT/'public/vo/us-v1';out.mkdir(parents=True,exist_ok=True)
profile=json.loads((ROOT/'src/config/performance-us-v1.json').read_text())
def norm(s):return ''.join(c for c in s if unicodedata.category(c)[0] in 'LN')
def duration(p):
 with wave.open(str(p),'rb') as w:return w.getnframes()/w.getframerate()
torch.set_num_threads(4)
model=whisper.load_model('tiny',device='cpu',download_root=str(ROOT/'.model-cache'))
tokenizer=get_tokenizer(multilingual=model.is_multilingual,num_languages=model.num_languages,language='en',task='transcribe')
records={}
for c in profile['auditions']:
 source=src/c['sourceFile'];target=out/f"audition-{c['id']}.wav"
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(source),'-ar','48000','-ac','1','-c:a','pcm_s16le',str(target)],check=True)
 seconds=duration(target);audio=whisper.load_audio(str(target));n_frames=len(audio)//whisper.audio.HOP_LENGTH
 mel=whisper.log_mel_spectrogram(whisper.pad_or_trim(audio),n_mels=model.dims.n_mels)
 words=find_alignment(model,tokenizer,tokenizer.encode(profile['auditionText']),mel,n_frames)
 (q/f"audition-{c['id']}-reference-alignment.json").write_text(json.dumps([{'word':w.word,'start':float(w.start),'end':float(w.end),'probability':float(w.probability)} for w in words],indent=2))
 chars=[]
 for w in words:
  word=norm(w.word)
  for i,ch in enumerate(word):chars.append((ch,float(w.start+(w.end-w.start)*i/max(1,len(word))),float(w.start+(w.end-w.start)*(i+1)/max(1,len(word)))))
 assert ''.join(c[0] for c in chars)==norm(profile['auditionText'])
 cursor=0;timings=[]
 for text in profile['subtitleChunks']:
  n=len(norm(text));start=max(0,chars[cursor][1]);end=min(seconds,chars[cursor+n-1][2]);cursor+=n
  timings.append({'text':text,'start':round(start,6),'end':round(end,6)})
 assert all(0<=t['start']<t['end']<=seconds for t in timings),timings
 records[c['id']]={'role':'audition_only_not_person_testimonial','voiceDisplayName':c['voiceDisplayName'],'nativeLanguageTag':c['nativeLanguageTag'],'language':'en-US','duration':seconds,'chunks':timings,'playbackRate':1,'synthesisSpeed':1,'synthesisPitch':0,'synthesisVolume':1,'mp3':str(source.relative_to(ROOT)),'wav':str(target.relative_to(ROOT)),'sourceMp3Sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'timingSource':'Local Whisper tiny English reference-text forced alignment; approximate, not independently measured error'}
 print(c['id'],seconds,timings,flush=True)
(ROOT/'src/config/vo-us-v1-timing.json').write_text(json.dumps(records,indent=2))
(out/'VOICE_PROVENANCE.json').write_text(json.dumps({'provider':'MiniMax website','url':'https://www.minimax.io/audio/text-to-speech','model':'speech-2.8-hd','languageControl':'English - detected','accentSource':'Native US voice library tags; not a separate US locale control','parameters':{'speed':1,'pitch':0,'volume':1,'playbackRate':1},'finalVoice':profile.get('voiceDisplayName'),'userSelection':profile.get('voiceSelectionStatus','pending'),'productionNarration':profile.get('productionNarration'),'source':'Downloaded original MP3 using MiniMax website menu in user Chrome; no TTS API or voice cloning used','authorization':'User adopted Prompt13, which calls for three same-text voice auditions','creditsObserved':profile['creditsObserved'],'timingAccuracy':'No <0.35ms accuracy claim; no ground truth available','segments':records},indent=2))
