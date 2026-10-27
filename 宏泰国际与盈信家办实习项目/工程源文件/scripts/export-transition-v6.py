"""Non-destructive timing derivative from v4. No TTS, text or artwork edits.
Speed only transition regions; remove idle holds after speech; preserve slower speech.
"""
from pathlib import Path
import subprocess,json,math,hashlib,wave
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'out/BOI-HK_MiniMax粵語_中英Logo_v4.mp4'
OUTPUT=ROOT/'out/BOI-HK_MiniMax粵語_快轉場自然語速_v6.mp4'
Q=ROOT/'qa/v6';PARTS=Q/'parts';PARTS.mkdir(parents=True,exist_ok=True)
FPS=30;RATE=1.12;POST=.65;END_HOLD=2.0
base=json.loads((ROOT/'qa/v4/content-audit.json').read_text())
voices=json.loads((ROOT/'public/vo/hk-v4/VOICE_PROVENANCE.json').read_text())['segments']
protected=list((ROOT/'src').rglob('*'))+list((ROOT/'public/vo/hk-v4').glob('*.wav'))+[SOURCE,ROOT/'out/BOI-HK_MiniMax粵語_59秒加速_v5.mp4']
hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in protected if p.is_file()}
(Q/'baseline-hashes.json').write_text(json.dumps(hashes,ensure_ascii=False,indent=2))
plan=[]
for s in base['scenes']:
 start,end=s['from'],s['end']
 if s['id']=='S0':
  ranges=[(start,306,240,'logo growth and hold'),(306,end,12,'logo exit transition')]
 else:
  rec=voices[f"vo/hk-v4/VO-{int(s['id'][1:]):02d}.wav"]
  speech_start=s['voiceStartFrame'];speech_end=speech_start+rec['duration']*FPS
  keep_end=math.ceil(speech_end+(END_HOLD*RATE if s['id']=='S7' else POST)*FPS)
  assert keep_end<end-12 or s['id']=='S7'
  ranges=[(start,start+10,5,'entry transition'),(start+10,keep_end,round((keep_end-start-10)/RATE),'speech and short hold')]
  if s['id']!='S7':ranges.append((end-12,end,6,'exit transition'))
 cursor=sum(x['frames']for x in plan)
 segments=[{'sourceFrom':a,'sourceTo':b,'outputFrames':n,'rate':(b-a)/n,'role':role}for a,b,n,role in ranges]
 scene={'id':s['id'],'from':cursor,'frames':sum(x['outputFrames']for x in segments),'segments':segments}
 if s['id']!='S0':
  speech=segments[1];scene['speechRate']=speech['rate'];scene['voiceFrom']=cursor+5+(speech_start-speech['sourceFrom'])/speech['rate'];scene['voiceEnd']=scene['voiceFrom']+rec['duration']*FPS/speech['rate']
 plan.append(scene)
frames=sum(s['frames']for s in plan)
report={'source':str(SOURCE),'output':str(OUTPUT),'fps':FPS,'frames':frames,'duration':frames/FPS,'nominalSpeechRate':RATE,'v5SpeechRate':751/590,'speechSlowerThanV5Percent':(1-RATE/(751/590))*100,'entryTransitionSeconds':5/FPS,'exitTransitionSeconds':6/FPS,'logoExitSeconds':12/FPS,'scenes':plan}
(Q/'timing-plan.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
for scene in plan:
 n=len(scene['segments']);vp=PARTS/f"{scene['id']}.mp4";ap=PARTS/f"{scene['id']}.wav"
 graph=[f"[0:v]split={n}"+''.join(f'[v{i}]'for i in range(n)),f"[0:a]asplit={n}"+''.join(f'[a{i}]'for i in range(n))]
 for i,x in enumerate(scene['segments']):
  a,b,nf,r=x['sourceFrom'],x['sourceTo'],x['outputFrames'],x['rate'];sec=nf/FPS
  graph.append(f"[v{i}]trim=start_frame={a}:end_frame={b},setpts=(PTS-STARTPTS)/{r:.16g},fps=30,trim=end_frame={nf},setpts=PTS-STARTPTS[vo{i}]")
  graph.append(f"[a{i}]atrim=start_sample={a*1600}:end_sample={b*1600},asetpts=PTS-STARTPTS,atempo={r:.16g},apad=whole_dur={sec:.12f},atrim=duration={sec:.12f},asetpts=PTS-STARTPTS[ao{i}]")
 graph.append(''.join(f'[vo{i}][ao{i}]'for i in range(n))+f'concat=n={n}:v=1:a=1[v][a]')
 graphfile=PARTS/f"{scene['id']}-filter.txt";graphfile.write_text(';\n'.join(graph))
 subprocess.run(['ffmpeg','-v','error','-nostdin','-y','-i',str(SOURCE),'-filter_complex_script',str(graphfile),'-map','[v]','-an','-c:v','libx264','-preset','slow','-crf','14','-pix_fmt','yuv420p',str(vp),'-map','[a]','-vn','-c:a','pcm_s16le','-ar','48000',str(ap)],check=True)
 actual=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(vp)]))['streams'][0]
 assert int(actual['nb_frames'])==scene['frames'],(scene['id'],actual['nb_frames'],scene['frames'])
 with wave.open(str(ap),'rb')as w:assert w.getnframes()==scene['frames']*1600,(scene['id'],w.getnframes())
 print(scene['id'],scene['frames'],'frames',flush=True)
(PARTS/'video-list.txt').write_text(''.join(f"file '{s['id']}.mp4'\n"for s in plan))
(PARTS/'audio-list.txt').write_text(''.join(f"file '{s['id']}.wav'\n"for s in plan))
subprocess.run(['ffmpeg','-v','error','-nostdin','-n','-f','concat','-safe','0','-i',str(PARTS/'video-list.txt'),'-f','concat','-safe','0','-i',str(PARTS/'audio-list.txt'),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','256k','-ar','48000','-movflags','+faststart',str(OUTPUT)],check=True)
changed=[p for p,h in hashes.items()if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h];assert not changed,changed
print('DONE',frames,'frames',frames/FPS,'seconds; source files unchanged',flush=True)
