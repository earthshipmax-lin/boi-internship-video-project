from pathlib import Path
import json,subprocess,hashlib
V=Path(__file__).resolve().parents[1];Q=V/'qa/v20';report={}
for loc in ['cn','yue','en']:
 t=json.load(open(V/f'src/config/timeline-v20-{loc}.json'));c=t['cues'];report[loc]={'frames':t['durationInFrames'],'seconds':t['durationSeconds'],'cueCount':len(c),'noPeopleScene':'people' not in t['sceneStarts'],'noPeopleCues':all(not x['id'].startswith('people-') for x in c),'noOverlaps':all(a['endFrame']<=b['startFrame'] for a,b in zip(c,c[1:])),'maximumInternalSubtitleGapSeconds':max((b['startFrame']-a['endFrame'])/30 for a,b in zip(c,c[1:])),'holdAfterSpeechSeconds':t['edit']['fadeStart']/30-next(x['speechEnd'] for x in c if x['id']=='caption-20'),'loudness':{}}
 for variant in ['A','B']:
  p=V/f'public/music/hk-v20/{loc}-candidate-{variant}.wav';r=subprocess.run(['ffmpeg','-hide_banner','-i',str(p),'-af','loudnorm=I=-16:TP=-1:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True);m=json.JSONDecoder().raw_decode(r.stderr[r.stderr.rfind('{'):])[0];report[loc]['loudness'][variant]={'LUFS':m['input_i'],'truePeakDBTP':m['input_tp']}
protected=json.load(open(Q/'protected.json'));bad=[p for p,h in protected.items() if hashlib.sha256((V.parent/p).read_bytes()).hexdigest()!=h];report['protected']={'count':len(protected),'changed':bad};assert not bad
(Q/'verification-progress.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
