from pathlib import Path
import subprocess,json,time
V=Path(__file__).resolve().parents[1];Q=V/'qa/v13/redesign';D=Q/'before-track-phase';D.mkdir(exist_ok=True)
t=json.loads((V/'src/config/timeline-v13-redesign.json').read_text());old=t['sourceTimeline']
def mapframe(f):
 n=f+sum(h['frames'] for h in old['holds'] if h['sourceFrame']<=f);return n-sum(min(c['frames'],max(0,n-c['startFrame'])) for c in t['redesignCuts'])
start,end=mapframe(431),mapframe(618)
def ready(p,frames):
 if not p.exists():return False
 r=subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames','-of','json',str(p)],capture_output=True,text=True)
 return r.returncode==0 and any(int(s.get('nb_frames',0))==frames for s in json.loads(r.stdout).get('streams',[]))
for loc,label in [('yue','粵語'),('en','英文'),('zh-CN','簡中')]:
 p=V/f'out/BOI-HK_史詩形象片_v13_{label}_重設計版.mp4';patch=Q/f'track-patch/{loc}.mp4';archive=D/p.name;out=Q/f'track-patch/{loc}-assembled.mp4'
 assert not archive.exists() and not out.exists()
 while not (ready(p,t['durationInFrames']) and ready(patch,end-start)):time.sleep(5)
 p.rename(archive)
 graph=f'[0:v]trim=end_frame={start},setpts=PTS-STARTPTS[a];[1:v]setpts=PTS-STARTPTS[b];[0:v]trim=start_frame={end},setpts=PTS-STARTPTS[c];[a][b][c]concat=n=3:v=1:a=0[v]'
 subprocess.run(['ffmpeg','-v','error','-n','-i',str(archive),'-i',str(patch),'-filter_complex',graph,'-map','[v]','-map','0:a:0','-c:v','libx264','-preset','fast','-crf','18','-threads','4','-pix_fmt','yuv420p','-r','30','-fps_mode','cfr','-c:a','copy','-movflags','+faststart',str(out)],check=True)
 assert ready(out,t['durationInFrames']);out.rename(p);print('FINAL TRACK PHASE',loc,flush=True)
(Q/'track-patch/ASSEMBLY.json').write_text(json.dumps({'frames':[start,end-1],'framesReplaced':end-start,'bankTrackPhasePx':-850,'originalRenderArchived':str(D.relative_to(V)),'audioCopiedUnchanged':True,'videoReencodedCRF':18},indent=2)+'\n')
