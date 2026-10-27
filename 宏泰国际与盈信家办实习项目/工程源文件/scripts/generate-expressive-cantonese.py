"""V2 Cantonese neural narration. User explicitly authorized Microsoft online TTS.
No acceleration to fit a preset duration. Source words remain unchanged.
"""
from pathlib import Path
import asyncio,subprocess,json,hashlib,re,wave,array,sys
import edge_tts
ROOT=Path(__file__).resolve().parents[1]
profile=json.loads((ROOT/'src/config/performance-hk-v2.json').read_text())
source=ROOT/'qa/v2/neural-source';source.mkdir(parents=True,exist_ok=True)
out=ROOT/'public/vo/hk-v2';out.mkdir(exist_ok=True)
VOICE=profile['onlineVoice']
def run(*args):return subprocess.run(list(map(str,args)),check=True,capture_output=True,text=True)
def duration(p):return float(run('ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',p).stdout)
def trim_service_padding(path):
 # Remove only service-added leading/trailing digital silence. Preserve consonants
 # plus 100ms lead and 180ms decay, then add the intentional performance pauses.
 with wave.open(str(path),'rb') as w:
  sr=w.getframerate();channels=w.getnchannels();width=w.getsampwidth();raw=w.readframes(w.getnframes())
 assert channels==1 and width==2
 samples=array.array('h',raw)
 if sys.byteorder!='little':samples.byteswap()
 block=480
 active=[i for i in range(0,len(samples),block) if max((abs(x) for x in samples[i:i+block]),default=0)>64]
 if not active:raise RuntimeError('Empty synthesis segment')
 start=max(0,active[0]-round(sr*.1));end=min(len(samples),active[-1]+block+round(sr*.18))
 with wave.open(str(path),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(raw[start*2:end*2])
async def main():
 sem=asyncio.Semaphore(2)
 async def synth(scene,i,cue):
  mp3=source/f'{scene}-{i}.mp3';wav=source/f'{scene}-{i}.wav'
  # Retry at most once on a transient service failure; no payment or publish action.
  async with sem:
   for attempt in range(2):
    if mp3.exists():break
    try:
     speaker=edge_tts.Communicate(cue['text'],VOICE,rate=cue['rate'],pitch=cue['pitch'],volume='-3%',connect_timeout=10,receive_timeout=25)
     await asyncio.wait_for(speaker.save(str(mp3)),timeout=40)
     break
    except Exception:
     if attempt:raise
     await asyncio.sleep(1)
   run('ffmpeg','-v','error','-y','-i',mp3,'-ar','48000','-ac','1','-c:a','pcm_s16le',wav)
   trim_service_padding(wav)
   print(scene,i,'ready',flush=True)
 await asyncio.gather(*(synth(scene,i,cue) for scene,cues in profile['scenes'].items() for i,cue in enumerate(cues)))
 records={}
 for scene,cues in profile['scenes'].items():
  parts=[];timings=[];cursor=0
  for i,cue in enumerate(cues):
   wav=source/f'{scene}-{i}.wav';seconds=duration(wav);parts.append(wav)
   timings.append({'text':cue['text'],'start':cursor,'end':cursor+seconds,'rate':cue['rate'],'pitch':cue['pitch']});cursor+=seconds
   if i<len(cues)-1:
    pause=source/f'{scene}-pause-{i}.wav';run('ffmpeg','-v','error','-y','-f','lavfi','-i','anullsrc=r=48000:cl=mono','-t',cue['pauseAfter'],pause);parts.append(pause);cursor+=cue['pauseAfter']
  concat=source/f'{scene}-concat.txt';concat.write_text(''.join("file '"+p.name+"'\n"for p in parts))
  filename=f'vo/hk-v2/VO-{int(scene[1:]):02d}.wav';target=ROOT/'public'/filename
  run('ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',concat,'-af','loudnorm=I=-18:TP=-2:LRA=7','-ar','48000','-ac','1',target)
  records[filename]={'language':'yue-HK','voice':VOICE,'provider':'Microsoft online neural TTS','authorization':'Explicit user approval in this chat','duration':duration(target),'chunks':timings,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'playbackRate':1}
  print(scene,round(records[filename]['duration'],3),'seconds; playbackRate=1',flush=True)
 (ROOT/'src/config/vo-hk-timing.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
 (out/'VOICE_PROVENANCE.json').write_text(json.dumps({'provider':'Microsoft online neural TTS via edge-tts 7.3.1','voice':VOICE,'purpose':'Warm Cantonese neural preview; no cloned or impersonated voice','textTransmission':'Only the user-approved narration phrases sent to Microsoft','segments':records},ensure_ascii=False,indent=2))
 # Keep scene minimums for breathing room; never ask speech to fit a scene.
 minimums={'S1':7.2,'S2':7.4,'S3':10,'S4':11,'S5':5,'S6':13,'S7':9.5}
 configpath=ROOT/'src/config/hk.ts';config=configpath.read_text();start=12;timeline=[]
 for scene,minimum in minimums.items():
  rec=records[f'vo/hk-v2/VO-{int(scene[1:]):02d}.wav'];tail=1.5 if scene=='S7' else .8
  frames=max(round(minimum*30),int((.35+rec['duration']+tail)*30+.9999));end=round(start+frames/30,6)
  config=re.sub(r"(id:'"+scene+r"',start:)[\d.]+(,end:)[\d.]+",lambda m:m[1]+str(start)+m[2]+str(end),config)
  timeline.append({'id':scene,'start':start,'end':end,'frames':frames,'voiceDuration':rec['duration'],'speechPlaybackRate':1});start=end
 config=re.sub(r'height:1080,duration:[\d.]+,chineseOnly',f'height:1080,duration:{start},chineseOnly',config)
 config=config.replace("provider:'pending expressive Cantonese v2'",f"provider:'Microsoft {VOICE}'").replace('subtitle:{leadIn:.25,tail:.2','subtitle:{leadIn:.35,tail:.3')
 configpath.write_text(config)
 (ROOT/'qa/v2/timeline.json').write_text(json.dumps({'duration':start,'fps':30,'speechAcceleration':False,'scenes':timeline},ensure_ascii=False,indent=2))
 print('Final natural duration:',start,'seconds',flush=True)
asyncio.run(main())
