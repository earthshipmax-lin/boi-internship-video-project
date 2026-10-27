from pathlib import Path
import json,subprocess
from PIL import Image,ImageDraw
V=Path(__file__).resolve().parents[1];Q=V/'qa/v15';D=Q/'encoded-frames';D.mkdir(exist_ok=True)
paths={l:V/f'out/BOI-HK_史詩形象片_v15_{n}_細節與聲音精修版.mp4' for l,n in [('yue','粵語'),('en','英文'),('cn','簡中')]}
t=json.loads((V/'src/config/timeline-v15-yue.json').read_text());cn=json.loads((V/'src/config/timeline-v15-cn.json').read_text())
ranges=[('yue',next(c['startFrame'] for c in t['cues'] if c['id']=='caption-16')/30-.2,t['sceneStarts']['paper']/30+1.2),('yue',next(c['startFrame'] for c in t['cues'] if c['id']=='people-operations-compliance')/30-.2,next(c['endFrame'] for c in t['cues'] if c['id']=='people-operations-compliance')/30+.15),('yue',next(c['startFrame'] for c in t['cues'] if c['id']=='people-partner-wall')/30-.2,next(c['endFrame'] for c in t['cues'] if c['id']=='people-partner-wall')/30+.15),('cn',min(c['startFrame'] for c in cn['cues'] if c['id']=='caption-23')/30-.3,cn['durationSeconds'])]
graph=[];concat=[]
for i,(loc,a,b) in enumerate(ranges):
 idx=0 if loc=='yue' else 1;graph.extend([f'[{idx}:v]trim=start={a}:end={b},setpts=PTS-STARTPTS[v{i}]',f'[{idx}:a]atrim=start={a}:end={b},asetpts=PTS-STARTPTS[a{i}]']);concat.append(f'[v{i}][a{i}]')
graph.append(''.join(concat)+'concat=n=4:v=1:a=1[v][a]');out=V/'out/BOI-HK_v15_中心轉場與人物及普通話片尾_重點預覽.mp4';assert not out.exists()
subprocess.run(['ffmpeg','-v','error','-n','-i',str(paths['yue']),'-i',str(paths['cn']),'-filter_complex',';'.join(graph),'-map','[v]','-map','[a]','-c:v','libx264','-preset','fast','-crf','18','-threads','4','-c:a','aac','-b:a','256k','-ar','48000','-r','30','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],check=True)
subprocess.run(['ffmpeg','-v','error','-i',str(out),'-f','null','-'],check=True,capture_output=True)
frames=[('yue',90),('yue',t['sceneStarts']['iris']+3),('yue',t['sceneStarts']['iris']+12),('yue',2204),('yue',2510),('cn',2835)]
canvas=Image.new('RGB',(1920,1710),'#142632');draw=ImageDraw.Draw(canvas)
for i,(loc,f) in enumerate(frames):
 f=round(f);p=D/f'{loc}-f{f}.png';subprocess.run(['ffmpeg','-v','error','-y','-ss',str(f/30),'-i',str(paths[loc]),'-frames:v','1',str(p)],check=True)
 x=i%2*960;y=i//2*570;canvas.paste(Image.open(p).resize((960,540)),(x,y+30));draw.text((x+12,y+8),f'FINAL ENCODED / {loc} / {f/30:.3f}s',fill='white')
canvas.save(Q/'actual-storyboard.jpg',quality=94)
for name,f in [('pamela',2204),('partners',2510)]:
 old=V/'out/BOI-HK_史詩形象片_v14_粵語_節奏與同步精修版.mp4';before=D/f'v14-f{f}.png';subprocess.run(['ffmpeg','-v','error','-y','-ss',str(f/30),'-i',str(old),'-frames:v','1',str(before)],check=True)
 after=D/f'yue-f{f}.png';canvas=Image.new('RGB',(1920,570),'#142632');draw=ImageDraw.Draw(canvas)
 for i,p in enumerate([before,after]):canvas.paste(Image.open(p).resize((960,540)),(i*960,30));draw.text((i*960+12,8),'V14 / BEFORE' if i==0 else 'V15 / AFTER',fill='white')
 canvas.save(Q/f'{name}-before-after.jpg',quality=94)
(Q/'preview.json').write_text(json.dumps({'file':str(out.relative_to(V)),'ranges':ranges,'completeDecode':True,'purpose':'Centered iris, corrected portraits and Mandarin re-recorded ending. All four excerpt ranges include complete spoken phrases with pre-roll and tails.'},ensure_ascii=False,indent=2)+'\n');print(out.name)
