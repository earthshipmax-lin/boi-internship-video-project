from pathlib import Path
import subprocess,json,hashlib,sys,numpy as np
R=Path(__file__).resolve().parents[1];q=R/'qa/us-v1-voice-b';src=R/'out/US-Team-v1-visual-study.mp4';vo=R/'public/vo/us-v1/team-b/VO-01.wav';master=q/'review-voice-master.wav';out=R/'out/US-Team-v1-B-narrated.mp4'
verify_only='--verify-only' in sys.argv
if out.exists() and not verify_only:raise RuntimeError('Refuse overwrite '+str(out))
rec=json.loads((vo.parent/'VOICE_PROVENANCE.json').read_text());assert rec['timelineEnd']<7.65 and rec['parameters']['playbackRate']==1
if not verify_only:
 subprocess.run(['ffmpeg','-v','error','-i',str(vo),'-af','adelay=800:all=1,apad=whole_dur=8,atrim=end=8','-ar','48000','-c:a','pcm_s16le',str(master)],check=True)
 subprocess.run(['ffmpeg','-v','error','-i',str(src),'-i',str(master),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',str(out)],check=True)
subprocess.run(['ffmpeg','-v','error','-i',str(out),'-f','null','-'],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(out)]));v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio');assert v['nb_frames']=='240' and v['width']==1920 and v['height']==1080 and float(probe['format']['duration'])==8
# All decoded frames must match the preserved silent MP4, since video packets are copied.
def framehash(p):return subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:v:0','-f','framemd5','-'])
assert framehash(src)==framehash(out)
def pcm(p):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-ar','48000','-ac','1','-f','f32le','-']),dtype=np.float32)
x,y=pcm(master),pcm(out);n=min(len(x),len(y));corr=float(np.corrcoef(x[:n],y[:n])[0,1]);assert corr>.999
loud=subprocess.run(['ffmpeg','-hide_banner','-i',str(out),'-vn','-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True).stderr;l=json.JSONDecoder().raw_decode(loud[loud.rindex('{'):])[0];assert float(l['input_tp'])<0
base=json.loads((q/'baseline.json').read_text());changed=[p for p,h in base.items() if hashlib.sha256((R.parent/p).read_bytes()).hexdigest()!=h];assert set(changed)=={'video/src/Root.tsx','video/src/config/performance-us-v1.json','video/public/vo/us-v1/VOICE_PROVENANCE.json'},changed
root=(R/'src/Root.tsx').read_text();previous=(q/'before/Root.tsx').read_text();root=root.replace("import {USTeamVoiceB} from './scenes/USTeamVoiceB';\n",'').replace('<Composition id="US-Team-v1-VoiceB" component={USTeamVoiceB} width={1920} height={1080} fps={30} durationInFrames={240}/>','');assert root==previous
r={'status':'technical_checks_passed_subjective_review_pending','composition':'US-Team-v1-VoiceB','output':str(out.relative_to(R)),'duration':8,'frames':240,'voice':'B / Magnetic-voiced Male - Deep,Resonant,Polished','voiceSourceDuration':rec['duration'],'voiceTimelineStart':.8,'voiceTimelineEnd':rec['timelineEnd'],'synthesisSpeed':1,'playbackRate':1,'originalVideoAll240DecodedFramesIdentical':True,'audioMasterCorrelation':corr,'loudnessLUFS':l['input_i'],'truePeakDBTP':l['input_tp'],'music':'none, voice-led pilot','protectedBaselineCount':len(base),'changedProtectedFiles':changed,'HKUnchanged':True,'originalUSSilentFilmUnchanged':True,'rootOnlyAdditive':True,'outputSha256':hashlib.sha256(out.read_bytes()).hexdigest()};(q/'verification.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
