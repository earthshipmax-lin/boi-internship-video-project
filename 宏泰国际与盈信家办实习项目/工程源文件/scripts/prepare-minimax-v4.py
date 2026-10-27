"""Prepare browser-generated MiniMax audio, with local reference-text alignment.
Never calls a TTS API. Requires existing local whisper/torch environment.
"""
from pathlib import Path
import json,subprocess,hashlib,re,math,unicodedata,wave
import torch, whisper
from whisper.timing import find_alignment
from whisper.tokenizer import get_tokenizer
ROOT=Path(__file__).resolve().parents[1];q=ROOT/'qa/v4';src=q/'minimax-source';out=ROOT/'public/vo/hk-v4';out.mkdir(parents=True,exist_ok=True)
profile=json.loads((ROOT/'src/config/performance-hk-v4.json').read_text())
def norm(s):return ''.join(c for c in s if unicodedata.category(c)[0] in 'LN')
def duration(p):
 with wave.open(str(p),'rb') as w:return w.getnframes()/w.getframerate()
torch.set_num_threads(4)
model=whisper.load_model('tiny',device='cpu',download_root=str(ROOT/'.model-cache'))
tokenizer=get_tokenizer(multilingual=model.is_multilingual,num_languages=model.num_languages,language='zh',task='transcribe')
records={}
for scene,c in profile['scenes'].items():
 source=src/f'{scene}.mp3';filename=f'vo/hk-v4/VO-{int(scene[1:]):02d}.wav';target=ROOT/'public'/filename
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(source),'-ar','48000','-ac','1','-c:a','pcm_s16le',str(target)],check=True)
 seconds=duration(target);audio=whisper.load_audio(str(target));n_frames=len(audio)//whisper.audio.HOP_LENGTH
 mel=whisper.log_mel_spectrogram(whisper.pad_or_trim(audio),n_mels=model.dims.n_mels)
 words=find_alignment(model,tokenizer,tokenizer.encode(c['text']),mel,n_frames)
 (q/f'{scene}-reference-alignment.json').write_text(json.dumps([{'word':w.word,'start':float(w.start),'end':float(w.end),'probability':float(w.probability)} for w in words],ensure_ascii=False,indent=2))
 chars=[]
 for w in words:
  word=norm(w.word)
  for i,ch in enumerate(word):chars.append((ch,float(w.start+(w.end-w.start)*i/max(1,len(word))),float(w.start+(w.end-w.start)*(i+1)/max(1,len(word)))))
 assert ''.join(c[0] for c in chars)==norm(c['text']),scene
 cursor=0;timings=[]
 for text in c['subtitleChunks']:
  n=len(norm(text));start=max(0,chars[cursor][1]);end=min(seconds,chars[cursor+n-1][2]);cursor+=n
  timings.append({'text':text,'start':round(start,6),'end':round(end,6)})
 assert all(0<=t['start']<t['end']<=seconds for t in timings),(scene,timings)
 records[filename]={'language':'yue-HK','voice':profile['voiceDisplayName'],'provider':'MiniMax website speech-2.8-hd','authorization':'User explicitly requested MiniMax in Chrome; approved S7 audition and requested same voice for all narration','duration':seconds,'chunks':timings,'synthesisSpeed':profile['speed'],'synthesisPitch':profile['pitch'],'emotions':c['emotions'],'synthesisUnit':'one complete scene; approved original S7 reused','timingSource':'Local Whisper tiny reference-text forced alignment; not provider timestamps or independent Cantonese transcription; cue-level review required','sourceMp3Sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'playbackRate':1}
 print(scene,seconds,'seconds',timings,flush=True)
(ROOT/'src/config/vo-hk-timing.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
(out/'VOICE_PROVENANCE.json').write_text(json.dumps({'provider':profile['provider'],'model':profile['model'],'voice':profile['voiceDisplayName'],'language':profile['language'],'parameters':{'speed':.95,'pitch':0,'volume':1},'userApproval':profile['userFeedback'],'creditsObserved':profile['creditsObserved'],'source':'Downloaded through MiniMax website MP3 menu in user-authorized Chrome tab; no API credentials used','segments':records},ensure_ascii=False,indent=2))
minimums={'S1':7.2,'S2':7.4,'S3':10,'S4':11,'S5':5,'S6':13,'S7':9.5}
configpath=ROOT/'src/config/hk.ts';config=configpath.read_text();frame=360;timeline=[]
for scene,minimum in minimums.items():
 rec=records[f'vo/hk-v4/VO-{int(scene[1:]):02d}.wav'];tail=1.8 if scene=='S7' else .8
 frames=max(round(minimum*30),math.ceil((.35+rec['duration']+tail)*30));start=round(frame/30,6);frame+=frames;end=round(frame/30,6)
 config=re.sub(r"(id:'"+scene+r"',start:)[\d.]+(,end:)[\d.]+",lambda m:m[1]+str(start)+m[2]+str(end),config)
 timeline.append({'id':scene,'start':start,'end':end,'frames':frames,'voiceDuration':rec['duration'],'speechPlaybackRate':1})
config=re.sub(r'height:1080,duration:[\d.]+,chineseOnly',f'height:1080,duration:{frame/30},chineseOnly',config);configpath.write_text(config)
(q/'timeline.json').write_text(json.dumps({'duration':frame/30,'fps':30,'frames':frame,'speechAcceleration':False,'scenes':timeline},ensure_ascii=False,indent=2))
picks=[['S0',285]]+[[s['id'],round((s['start']+(s['end']-s['start'])*(.85 if s['id'] in ['S4','S6','S7'] else .5))*30)]for s in timeline]
(q/'qa-picks.json').write_text(json.dumps(picks,indent=2));print('Final film',frame/30,'seconds',frame,'frames')
