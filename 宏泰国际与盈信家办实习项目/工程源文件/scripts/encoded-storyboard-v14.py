from pathlib import Path
import json,subprocess
from PIL import Image,ImageDraw
V=Path(__file__).resolve().parents[1];Q=V/'qa/v14';D=Q/'encoded-frames';D.mkdir(exist_ok=True);t=json.loads((V/'src/config/timeline-v14-yue.json').read_text());s=t['sceneStarts']
frames=[90,round(s['data']+50),round(s['awards']+60),round(s['map']+160),round(s['platform']+20),round(s['platform']+110),round(s['people']+210),round(s['roots']+15),round(s['roots']+60),round(s['closing']+115)]
movie=V/'out/BOI-HK_史詩形象片_v14_粵語_節奏與同步精修版.mp4';canvas=Image.new('RGB',(1920,2850),'#142632');draw=ImageDraw.Draw(canvas)
for i,f in enumerate(frames):
 p=D/f'yue-f{f}.png';subprocess.run(['ffmpeg','-v','error','-y','-ss',str(f/30),'-i',str(movie),'-frames:v','1',str(p)],check=True)
 x=i%2*960;y=i//2*570;canvas.paste(Image.open(p).resize((960,540)),(x,y+30));draw.text((x+12,y+8),f'FINAL ENCODED / {f/30:.3f}s / frame {f}',fill='white')
canvas.save(Q/'actual-storyboard.jpg',quality=94);print('Actual encoded storyboard saved.')
