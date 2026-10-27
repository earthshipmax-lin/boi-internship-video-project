from pathlib import Path
import json,subprocess,re,hashlib,sys
import numpy as np
V=Path(__file__).resolve().parents[1];Q=V/'qa/v15'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
protected=json.loads((Q/'protected-baseline.json').read_text());changes=[p for p,h in protected.items() if not (V/p).is_file() or sha(V/p)!=h];assert not changes,changes
results=json.loads((Q/'verification.json').read_text())['results'] if '--locale=en' in sys.argv else {}
def pcm(p):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-f','f32le','-ar','48000','-ac','2','-']),dtype='<f4')
for loc,label in [('yue','粵語'),('en','英文'),('cn','簡中')]:
 if '--locale=en' in sys.argv and loc!='en':
  assert sha(V/results[loc]['file'])==results[loc]['sha256'];continue
 p=V/f'out/BOI-HK_史詩形象片_v15_{label}_細節與聲音精修版.mp4';t=json.loads((V/f'src/config/timeline-v15-{loc}.json').read_text())
 data=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]));video=next(s for s in data['streams'] if s['codec_type']=='video');audio=next(s for s in data['streams'] if s['codec_type']=='audio')
 assert (video['width'],video['height'],video['avg_frame_rate'],int(video['nb_frames']))==(1920,1080,'30/1',t['durationInFrames'])
 assert audio['sample_rate']=='48000' and audio['channels']==2
 subprocess.run(['ffmpeg','-v','error','-i',str(p),'-f','null','-'],capture_output=True,check=True)
 a=pcm(p);b=pcm(V/f'public/music/hk-v15/{loc}-master.wav');n=min(len(a),len(b));corr=float(np.corrcoef(a[:n],b[:n])[0,1]);assert corr>.999
 r=subprocess.run(['ffmpeg','-hide_banner','-i',str(p),'-af','loudnorm=I=-13.8:TP=-1.3:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True);m=json.loads(re.findall(r'\{\s*"input_i".*?\}',r.stderr,re.S)[-1]);assert float(m['input_tp'])<=-0.8
 assert -14.2<=float(m['input_i'])<=-13.4,(loc,m)
 results[loc]={'file':str(p.relative_to(V)),'sha256':sha(p),'bytes':p.stat().st_size,'frames':int(video['nb_frames']),'seconds':float(video['duration']),'containerSeconds':float(data['format']['duration']),'completeDecode':True,'audioCorrelationToMaster':corr,'integratedLUFS':float(m['input_i']),'truePeakDBTP':float(m['input_tp'])}
 print(loc,'VERIFIED',flush=True)
check=json.loads((Q/'preflight.json').read_text());assert all(not v['activeFramesOutsideSubtitles'] for v in check['sync'].values())
report={'status':'technical_delivery_pending_user_review','results':results,'protectedFilesUnchanged':len(protected),'protectedChanges':changes,'sourceScope':'HK V15 only; all prior V14 and US sources/renders retained','nativeFrameRecords':sum(v['sampleRecords'] for v in check['layout'].values()),'limits':['Frame activity coverage verifies subtitle boundaries, not a full human pronunciation review.','ASR is a content diagnostic; audience reception is not certified.','Native PNG and H264 are not pixel-identical.','Three locales have their own measured duration for natural pacing.']}
(Q/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'videos':3,'protectedUnchanged':len(protected)}))
