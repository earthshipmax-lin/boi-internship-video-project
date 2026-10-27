"""Local Cantonese preview voice, with exact script chunks and measured timings.
Requires macOS say / Sinji (zh_HK), ffmpeg and ffprobe. No external API calls.
"""
from pathlib import Path
import subprocess,re,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
config=(ROOT/'src/config/hk.ts').read_text();temp=ROOT/'qa/cantonese-source';temp.mkdir(exist_ok=True)
out=ROOT/'public/vo/hk';out.mkdir(exist_ok=True)
def run(*args):return subprocess.run(list(map(str,args)),check=True,capture_output=True,text=True)
def duration(p):return float(run('ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',p).stdout)
records={};gap=.12
for line in config.splitlines():
 if "vo:'vo/hk/" not in line:continue
 id=re.search(r"id:'([^']+)'",line)[1];file=re.search(r"vo:'([^']+)'",line)[1]
 chunks=re.findall(r"'([^']*)'",re.search(r"subtitleChunks:\[([^\]]+)\]",line)[1])
 start=float(re.search(r'start:([\d.]+)',line)[1]);end=float(re.search(r'end:([\d.]+)',line)[1]);slot=end-start-.25-.25
 rate=145;parts=[]
 for attempt in range(4):
  parts=[];timings=[];cursor=0
  for i,text in enumerate(chunks):
   aiff=temp/f'{id}-{i}.aiff';wav=temp/f'{id}-{i}.wav'
   run('say','-v','Sinji','-r',str(rate),'-o',aiff,text)
   run('ffmpeg','-v','error','-y','-i',aiff,'-ar','48000','-ac','1','-c:a','pcm_s16le',wav)
   seconds=duration(wav);timings.append({'text':text,'start':cursor,'end':cursor+seconds});cursor+=seconds;parts.append(wav)
   if i<len(chunks)-1:
    pause=temp/f'pause-{i}.wav';run('ffmpeg','-v','error','-y','-f','lavfi','-i','anullsrc=r=48000:cl=mono','-t',str(gap),pause);parts.append(pause);cursor+=gap
  if cursor<=slot:break
  rate=round(rate*(cursor/slot)*1.02)
 else:raise RuntimeError(f'{id}: voice cannot fit fixed timeline')
 target=ROOT/'public'/file
 # File list only contains generated ASCII basenames in this script's qa folder.
 concat=temp/f'{id}-concat.txt';concat.write_text(''.join("file '"+p.name+"'\n" for p in parts))
 run('ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',concat,'-af','loudnorm=I=-18:TP=-2:LRA=7','-ar','48000','-ac','1',target)
 actual=duration(target)
 records[file]={'language':'yue-HK','voice':'macOS Sinji (zh_HK)','rate':rate,'duration':actual,'chunks':timings,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
 print(id,rate,round(actual,3),'seconds / available',slot,flush=True)
(ROOT/'src/config/vo-hk-timing.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
(out/'VOICE_PROVENANCE.json').write_text(json.dumps({'provider':'macOS built-in Speech / Sinji','locale':'zh_HK','purpose':'Local synthetic Cantonese preview; not a commissioned professional voiceover','scriptSource':'BOI_60s_文案_繁中_v1.md','segments':records},ensure_ascii=False,indent=2))
