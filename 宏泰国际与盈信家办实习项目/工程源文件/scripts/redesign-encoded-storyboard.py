from pathlib import Path
import subprocess
from PIL import Image,ImageDraw
V=Path(__file__).resolve().parents[1];Q=V/'qa/v13/redesign';D=Q/'encoded-frames';D.mkdir(exist_ok=True)
frames=[96,563,681,984,1372,1634,1900,2400,2987,3250]
movie=V/'out/BOI-HK_史詩形象片_v13_粵語_重設計版.mp4'
sheet=Image.new('RGB',(1920,5*570),'#151b21');draw=ImageDraw.Draw(sheet)
for i,f in enumerate(frames):
 p=D/f'yue-f{f}.png'
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(f/30),'-i',str(movie),'-frames:v','1',str(p)],check=True)
 x=i%2*960;y=i//2*570
 sheet.paste(Image.open(p).resize((960,540)),(x,y+30));draw.text((x+16,y+8),f'FINAL ENCODED / {f/30:.3f}s / frame {f}',fill='white')
sheet.save(Q/'actual-storyboard.jpg',quality=94)
print('10 actual encoded frames saved.')
