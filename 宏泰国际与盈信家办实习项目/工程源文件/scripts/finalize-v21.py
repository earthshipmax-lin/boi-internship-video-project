from pathlib import Path
import json,subprocess,time,hashlib
V=Path(__file__).resolve().parents[1];Q=V/'qa/v21';plans=json.load(open(Q/'patch-plan.json'));results={}
def run(cmd):return subprocess.run(['ffmpeg','-v','error','-n',*cmd],check=True)
def audiohash(p):return subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-c','copy','-f','hash','-hash','sha256','-']).decode().strip()
def pcmhash(p):return subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-f','hash','-hash','sha256','-']).decode().strip()
def frames(p):
 r=subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:v','-f','framemd5','-']).decode();return [s.split(',')[-1].strip() for s in r.splitlines() if not s.startswith('#')]
for loc,label in [('cn','普通話'),('yue','粵語'),('en','英文')]:
 p=plans[loc]
 while f'READY {loc}' not in (Q/'render.log').read_text():time.sleep(3)
 old=V/p['old'];prefix=Q/f'{loc}-prefix.mp4';suffix=Q/f'{loc}-suffix.mp4';pic=Q/f'{loc}-picture.mp4';out=V/f'out/BOI-HK_史詩形象片_v21_{label}_統一樹生成長版.mp4';preview=V/f'out/BOI-HK_v21_{label}_樹生成長9秒預覽.mp4'
 run(['-i',str(old),'-map','0:v:0','-an','-c:v','copy','-frames:v',str(p['start']),str(prefix)])
 run(['-ss',str(p['end']/30),'-i',str(old),'-map','0:v:0','-an','-c:v','copy',str(suffix)])
 cat=Q/f'{loc}-concat.txt';cat.write_text('\n'.join(f"file '{loc}-{x}.mp4'" for x in ['prefix','patch','suffix'])+'\n');run(['-f','concat','-safe','0','-i',str(cat),'-c:v','copy',str(pic)])
 run(['-i',str(pic),'-i',str(old),'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',str(out)])
 run(['-ss',str(p['roots']/30-1),'-i',str(out),'-t','9','-c:v','libx264','-crf','18','-c:a','aac','-b:a','320k',str(preview)])
 for f in [out,preview]:subprocess.run(['ffmpeg','-v','error','-i',str(f),'-f','null','-'],check=True)
 a=frames(old);b=frames(out);assert len(a)==len(b)==p['frames'],(loc,len(a),len(b));assert a[:p['start']]==b[:p['start']];assert a[p['end']:]==b[p['end']:]
 ah=audiohash(old);bh=audiohash(out);assert ah==bh;pa=pcmhash(old);pb=pcmhash(out);assert pa==pb
 packet=lambda f:json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','a:0','-show_packets','-show_entries','packet=pts,dts,duration,size','-of','json',str(f)]))['packets']
 assert packet(old)==packet(out),'Audio packet timestamps changed'
 r={'file':str(out.relative_to(V)),'preview':str(preview.relative_to(V)),'frames':len(b),'seconds':len(b)/30,'sha256':hashlib.file_digest(out.open('rb'),'sha256').hexdigest(),'audioPacketBytesAndTimestampsEqual':True,'audioPCMEqual':True,'audioSHA256':ah,'audioPCMSHA256':pa,'videoFramesOutsidePatchEqual':True,'unchangedFrames':p['start']+len(b)-p['end'],'patch':[p['start'],p['end']-1],'fullDecodePassed':True};results[loc]=r;(Q/'deliverables.json').write_text(json.dumps(results,ensure_ascii=False,indent=2));print('DELIVERABLE',loc,flush=True)
