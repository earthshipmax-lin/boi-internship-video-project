from pathlib import Path
import subprocess,json,shutil
V=Path(__file__).resolve().parents[1];Q=V/'qa/v15';archive=Q/'visual-only-r02';archive.mkdir(exist_ok=True);report={}
for loc,label in [('yue','粵語'),('en','英文'),('cn','簡中')]:
 out=V/f'out/BOI-HK_史詩形象片_v15_{label}_細節與聲音精修版.mp4';source=archive/out.name
 assert not source.exists();shutil.move(str(out),str(source))
 assert len(json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(source)]))['streams'])==1
 subprocess.run(['ffmpeg','-v','error','-n','-i',str(source),'-i',str(V/f'public/music/hk-v15/{loc}-master.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','320k','-ar','48000','-movflags','+faststart',str(out)],check=True)
 data=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(out)]));assert {s['codec_type'] for s in data['streams']}=={'video','audio'}
 report[loc]={'visualStreamCopied':True,'audioMaster':f'public/music/hk-v15/{loc}-master.wav','audioCodec':'aac','audioBitrate':320000,'visualSource':str(source.relative_to(V))};print(loc,'AUDIO MUXED',flush=True)
(Q/'export-audio-repair.json').write_text(json.dumps({'cause':'Stills composition resolved muted:true; renderMedia inputProps did not override resolved composition props. Re-select full composition with muted:false in renderer for future reproduction. Final videos copied the complete rendered H264 picture and encoded approved mix WAV as AAC, followed by full verification.','results':report},indent=2)+'\n')
