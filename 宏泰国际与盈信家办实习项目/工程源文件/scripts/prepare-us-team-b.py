"""Prepare selected B narration without modifying historical auditions or HK files."""
from pathlib import Path
import json,subprocess,hashlib,wave
import torch,whisper
from whisper.timing import find_alignment
from whisper.tokenizer import get_tokenizer
R=Path(__file__).resolve().parents[1];q=R/'qa/us-v1-voice-b';out=R/'public/vo/us-v1/team-b'
p=json.loads((R/'src/config/performance-us-v1.json').read_text());c=p['scenes']['TEAM'];src=q/'team-b-source.mp3';wav=out/'VO-01.wav'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(src),'-ar','48000','-ac','1','-c:a','pcm_s16le',str(wav)],check=True)
with wave.open(str(wav),'rb') as w:duration=w.getnframes()/w.getframerate()
assert .8+duration<7.65, 'Narration must finish before visual fade; adjust wording or duration, never speed up.'
torch.set_num_threads(4);model=whisper.load_model('tiny',device='cpu',download_root=str(R/'.model-cache'));tokenizer=get_tokenizer(multilingual=model.is_multilingual,num_languages=model.num_languages,language='en',task='transcribe')
audio=whisper.load_audio(str(wav));n_frames=len(audio)//whisper.audio.HOP_LENGTH;mel=whisper.log_mel_spectrogram(whisper.pad_or_trim(audio),n_mels=model.dims.n_mels)
words=find_alignment(model,tokenizer,tokenizer.encode(c['text']),mel,n_frames)
word_records=[{'word':w.word,'start':float(w.start),'end':float(w.end),'probability':float(w.probability)} for w in words];(q/'reference-alignment.json').write_text(json.dumps(word_records,indent=2))
asr=model.transcribe(str(wav),language='en',fp16=False,verbose=None);(q/'independent-english-ASR.json').write_text(json.dumps({'text':asr['text'],'language':'en','model':'tiny','note':'Automated content check, not a human pronunciation or accent evaluation.'},indent=2))
rec={'provider':'MiniMax website','url':'https://www.minimax.io/audio/text-to-speech','model':'speech-2.8-hd','voiceDisplayName':p['voiceDisplayName'],'language':'en-US','languageControl':'English - detected','userSelection':'B chosen directly by user 2026-10-24','userFeedback':p['userFeedback'],'parameters':{'speed':1,'pitch':0,'volume':1,'playbackRate':1},'text':c['text'],'synthesisText':c['synthesisText'],'duration':duration,'timelineStart':.8,'timelineEnd':.8+duration,'subtitleChunks':c['subtitleChunks'],'wordAlignment':word_records,'alignmentMethod':'Local Whisper tiny English reference-text alignment; no sub-millisecond accuracy claim','mp3Sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'wavSha256':hashlib.sha256(wav.read_bytes()).hexdigest(),'creditsObserved':{'before':3015,'after':None},'rightsStatus':'Internal review only; final company copy/portrait approval pending'}
(out/'VOICE_PROVENANCE.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2));(R/'src/config/vo-us-team-b-timing.json').write_text(json.dumps({'source':'vo/us-v1/team-b/VO-01.wav','duration':duration,'startFrame':24,'fps':30,'playbackRate':1,'words':word_records},indent=2))
p['productionNarration']={'source':'vo/us-v1/team-b/VO-01.wav','provenance':'public/vo/us-v1/team-b/VOICE_PROVENANCE.json','duration':duration,'startFrame':24,'playbackRate':1};(R/'src/config/performance-us-v1.json').write_text(json.dumps(p,ensure_ascii=False,indent=2))
print('Duration',duration,'timeline .8 to',.8+duration,'ASR:',asr['text'])
