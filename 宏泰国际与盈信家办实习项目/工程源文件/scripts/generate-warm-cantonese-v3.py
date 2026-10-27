"""V3: continuous Cantonese speech; Microsoft text transmission authorized by user.
No artificial phrase joins, audio pitch shifts, or speech time compression.
"""
from pathlib import Path
import asyncio, subprocess, json, hashlib, re, wave, array, sys, math, html, unicodedata
import edge_tts
ROOT=Path(__file__).resolve().parents[1]
profile=json.loads((ROOT/'src/config/performance-hk-v3.json').read_text())
source=ROOT/'qa/v3/neural-source';source.mkdir(parents=True,exist_ok=True)
out=ROOT/'public/vo/hk-v3';out.mkdir(parents=True,exist_ok=True)
VOICE=profile['onlineVoice']
def run(*a):return subprocess.run(list(map(str,a)),check=True,capture_output=True,text=True)
def duration(p):return float(run('ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',p).stdout)
def normalize(s):return ''.join(c for c in html.unescape(s) if unicodedata.category(c)[0] in 'LN')
def trim_padding(path):
 with wave.open(str(path),'rb') as w:sr=w.getframerate();raw=w.readframes(w.getnframes());assert w.getnchannels()==1 and w.getsampwidth()==2
 samples=array.array('h',raw)
 if sys.byteorder!='little':samples.byteswap()
 active=[i for i in range(0,len(samples),480) if max(map(abs,samples[i:i+480]),default=0)>64]
 if not active:raise RuntimeError('Silent TTS output')
 start=max(0,active[0]-round(sr*.1));end=min(len(samples),active[-1]+480+round(sr*.2))
 with wave.open(str(path),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(raw[start*2:end*2])
 return start/sr
async def main():
 sem=asyncio.Semaphore(2)
 async def synth(scene,c):
  digest=hashlib.sha256(json.dumps([VOICE,c],ensure_ascii=False,sort_keys=True).encode()).hexdigest()[:16]
  mp3=source/f'{scene}-{digest}.mp3';meta=source/f'{scene}-{digest}.jsonl'
  async with sem:
   if not(mp3.exists() and meta.exists()):
    for attempt in range(2):
     try:
      # Save to staging files so a network failure cannot leave a reusable partial cache.
      partial=Path(str(mp3)+'.partial');events=Path(str(meta)+'.partial')
      speaker=edge_tts.Communicate(c['text'],VOICE,rate=c['rate'],pitch=c['pitch'],volume='-3%',boundary='WordBoundary',connect_timeout=10,receive_timeout=25)
      await asyncio.wait_for(speaker.save(str(partial),str(events)),timeout=45)
      if not partial.stat().st_size or not events.stat().st_size:raise RuntimeError('Empty TTS source')
      partial.replace(mp3);events.replace(meta);break
     except Exception:
      if attempt:raise
      await asyncio.sleep(1)
   wav=source/f'{scene}-raw.wav';run('ffmpeg','-v','error','-y','-i',mp3,'-ar','48000','-ac','1','-c:a','pcm_s16le',wav)
   trimmed=trim_padding(wav)
   target=out/f'VO-{int(scene[1:]):02d}.wav'
   run('ffmpeg','-v','error','-y','-i',wav,'-af','loudnorm=I=-18:TP=-2:LRA=7','-ar','48000','-ac','1','-c:a','pcm_s16le',target)
   seconds=duration(target)
   boundaries=[json.loads(line) for line in meta.read_text().splitlines() if line.strip()]
   boundaries=[b for b in boundaries if b['type']=='WordBoundary']
   chars=[]
   for b in boundaries:
    word=normalize(b['text']);start=b['offset']/1e7-trimmed;dur=b['duration']/1e7
    for i,ch in enumerate(word):chars.append((ch,max(0,start+dur*i/max(1,len(word))),min(seconds,start+dur*(i+1)/max(1,len(word)))))
   expected=normalize(c['text']);got=''.join(x[0] for x in chars)
   if expected!=got:raise RuntimeError(f'{scene}: speech metadata text mismatch: {got!r} != {expected!r}')
   cursor=0;timings=[]
   for text in c['subtitleChunks']:
    n=len(normalize(text));assert n
    timings.append({'text':text,'start':round(chars[cursor][1],6),'end':round(chars[cursor+n-1][2],6)});cursor+=n
   assert cursor==len(chars)
   records[f'vo/hk-v3/{target.name}']={'language':'yue-HK','voice':VOICE,'provider':'Microsoft online neural TTS','authorization':'User explicitly authorized narration text transmission to Microsoft','duration':seconds,'chunks':timings,'rate':c['rate'],'pitch':c['pitch'],'synthesisUnit':'one complete scene, no phrase splicing','timingSource':'Microsoft WordBoundary metadata; word-internal character interpolation only when needed','trimmedLeadingPaddingSeconds':trimmed,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'playbackRate':1}
   print(scene,seconds,'seconds; continuous speech; metadata aligned',flush=True)
 records={}
 await asyncio.gather(*(synth(k,c) for k,c in profile['scenes'].items()))
 records=dict(sorted(records.items()))
 (ROOT/'src/config/vo-hk-timing.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
 (out/'VOICE_PROVENANCE.json').write_text(json.dumps({'provider':'Microsoft online neural TTS via edge-tts 7.3.1','voice':VOICE,'purpose':'Slightly brighter, gentle Cantonese voice candidate; subjective naturalness awaits user audition','textTransmission':'Only user-authorized narration text sent to Microsoft','segments':records},ensure_ascii=False,indent=2))
 # Preserve user-approved v2 scene lengths; extend only if natural speech needs more room.
 minimums={'S1':216,'S2':222,'S3':331,'S4':330,'S5':150,'S6':412,'S7':285}
 configpath=ROOT/'src/config/hk.ts';config=configpath.read_text();frame=360;timeline=[]
 for scene,minimum in minimums.items():
  rec=records[f'vo/hk-v3/VO-{int(scene[1:]):02d}.wav'];tail=1.8 if scene=='S7' else .8
  frames=max(minimum,math.ceil((.35+rec['duration']+tail)*30));start=frame/30;frame+=frames;end=frame/30
  config=re.sub(r"(id:'"+scene+r"',start:)[\d.]+(,end:)[\d.]+",lambda m:m[1]+str(round(start,6))+m[2]+str(round(end,6)),config)
  timeline.append({'id':scene,'start':start,'end':end,'frames':frames,'voiceDuration':rec['duration'],'speechPlaybackRate':1})
 config=re.sub(r'height:1080,duration:[\d.]+,chineseOnly',f'height:1080,duration:{frame/30},chineseOnly',config);configpath.write_text(config)
 (ROOT/'qa/v3/timeline.json').write_text(json.dumps({'duration':frame/30,'fps':30,'frames':frame,'speechAcceleration':False,'scenes':timeline},ensure_ascii=False,indent=2))
 picks=[['S0',285]]+[[s['id'],round((s['start']+(s['end']-s['start'])*(.85 if s['id'] in ['S4','S6','S7'] else .5))*30)] for s in timeline]
 (ROOT/'qa/v3/qa-picks.json').write_text(json.dumps(picks,indent=2))
 print('Final duration',frame/30,'seconds',frame,'frames',flush=True)
asyncio.run(main())
