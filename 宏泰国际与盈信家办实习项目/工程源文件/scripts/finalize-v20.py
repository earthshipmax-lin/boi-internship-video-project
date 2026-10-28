from pathlib import Path
import json,subprocess,time,shutil,hashlib
V=Path(__file__).resolve().parents[1];Q=V/'qa/v20';D=V/'public/music/hk-v20';O=V/'out'
(Q/'USER_SELECTION.json').write_text(json.dumps({'date':'2026-10-28','choice':'A','userReply':'A，然后三个语言的版本都要重做','audioPriority':'Preserve original loudness and PCM; overrides -16 LUFS target','music':'User accepted A equal-power bridge after disclosure that strict bar alignment cannot be certified','localOnly':True},ensure_ascii=False,indent=2))
results={}
for loc,label in [('cn','普通話'),('yue','粵語'),('en','英文')]:
 t=json.load(open(V/f'src/config/timeline-v20-{loc}.json'));audio=D/f'{loc}-master.wav';src=D/f'{loc}-candidate-A.wav'
 if not audio.exists():shutil.copyfile(src,audio)
 while f'{loc} 100%' not in (Q/'render.log').read_text():time.sleep(4)
 p=Q/f'{loc}-picture.mp4'
 while subprocess.run(['ffprobe','-v','error','-show_entries','format=duration',str(p)],capture_output=True).returncode:time.sleep(3)
 out=O/f'BOI-HK_史詩形象片_v20_{label}_無人物版.mp4'
 if not out.exists():subprocess.run(['ffmpeg','-v','error','-n','-i',str(p),'-i',str(audio),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','320k','-movflags','+faststart',str(out)],check=True)
 start=t['edit']['cutStart']/30-10;preview=O/f'BOI-HK_v20_{label}_接點20秒預覽.mp4'
 if not preview.exists():subprocess.run(['ffmpeg','-v','error','-n','-ss',str(start),'-i',str(out),'-t','20','-c:v','libx264','-crf','18','-c:a','aac','-b:a','320k',str(preview)],check=True)
 for f in [out,preview]:subprocess.run(['ffmpeg','-v','error','-i',str(f),'-f','null','-'],check=True)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(out)]));vs=next(s for s in probe['streams'] if s['codec_type']=='video');assert int(vs['nb_frames'])==t['durationInFrames']
 results[loc]={'file':str(out.relative_to(V)),'preview':str(preview.relative_to(V)),'sha256':hashlib.file_digest(out.open('rb'),'sha256').hexdigest(),'frames':int(vs['nb_frames']),'seconds':float(probe['format']['duration']),'decodePassed':True,'hasAudio':any(s['codec_type']=='audio' for s in probe['streams'])};(Q/'deliverables.json').write_text(json.dumps(results,ensure_ascii=False,indent=2));print('DELIVERABLE',loc,results[loc],flush=True)
