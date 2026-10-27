from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,json,hashlib,shutil,math
R=Path(__file__).resolve().parents[1];q=R/'qa/v12/stage2';out=R/'public/stills/v12/cut'
q.mkdir(parents=True,exist_ok=True);out.mkdir(parents=True,exist_ok=True);(q/'awards-cut').mkdir(exist_ok=True)
# The user-supplied rule explicitly specifies pixel threshold matting. Preserve
# source RGB and protect the foreground silhouettes, including pale reflections.
polygons={
1:[(39,39),(111,5),(168,4),(184,397),(188,418),(193,525),(5,525),(11,420),(18,398)],
2:[(11,26),(159,75),(137,416),(150,418),(177,525),(10,526),(21,451),(32,420),(55,419),(15,323),(39,244),(33,214)],
3:[(147,3),(240,201),(174,392),(188,405),(209,508),(41,508),(63,406),(83,397),(27,287),(23,278),(54,198)],
4:[(126,15),(137,13),(145,50),(163,82),(168,99),(179,111),(177,122),(164,134),(169,152),(173,170),(179,190),(194,205),(199,223),(184,239),(189,254),(178,270),(171,288),(166,306),(175,334),(182,355),(191,384),(199,409),(199,447),(194,484),(188,519),(30,520),(23,498),(19,468),(17,430),(15,390),(17,333),(20,280),(30,226),(38,185),(45,153),(52,115),(64,83),(84,48),(107,22)]}
heights=[300,290,295,300,260,260,240,260];assets=[]
for i in range(1,9):
 src=R/f'public/stills/v12/awards-{i:02}.jpg';im=Image.open(src).convert('RGB');rgb=np.array(im);hsv=np.array(im.convert('HSV'));bright=(rgb.astype(float)@np.array([.2126,.7152,.0722]))>235;neutral=hsv[:,:,1]<18;candidate=bright&neutral
 if i<=4:
  mask=Image.new('L',im.size);ImageDraw.Draw(mask).polygon(polygons[i],fill=255)
  # Neutral bright background outside the protected body is transparent; the
  # silhouette also removes source PPT blue/grid pixels that are not neutral.
  alpha=np.array(mask);protected=int(np.count_nonzero(candidate&(alpha>0)))
  mask=mask.filter(ImageFilter.GaussianBlur(.45));rgba=im.convert('RGBA');rgba.putalpha(mask)
  bbox=rgba.getbbox();rgba=rgba.crop(bbox);mode='threshold + protected silhouette, subpixel 1px fringe'
 else:
  # Certificates are whole pale objects. Their paper is not removable backdrop.
  rgba=Image.new('RGBA',(im.width+8,im.height+8),'#F4EEE2');rgba.alpha_composite(im.convert('RGBA'),(4,4));ImageDraw.Draw(rgba).rectangle((1,1,rgba.width-2,rgba.height-2),outline='#B8AA91',width=1);bbox=(0,0,im.width,im.height);protected=int(np.count_nonzero(candidate));mode='preserved certificate + 4px cream mount, 1px rule'
 dst=out/f'awards-{i:02}.png';rgba.save(dst)
 height=heights[i-1];width=rgba.width/rgba.height*height
 assert width<=im.width*1.2
 assets.append({'id':f'awards-{i:02}','file':f'stills/v12/cut/{dst.name}','original_pixels':list(im.size),'cut_pixels':list(rgba.size),'source_crop':bbox,'method':mode,'protected_bright_pixels':protected,'display_width':round(width,4),'display_height':height,'width_vs_original':round(width/im.width,4),'bottom':750})
 # Each comparison shows original, transparency checkerboard and dark composite.
 canvas=Image.new('RGB',(720,440),'#F4EEE2');draw=ImageDraw.Draw(canvas)
 for j,label in enumerate(['ORIGINAL','ALPHA','ON NAVY']):draw.text((j*240+12,10),label,fill='#243E50')
 a=im.copy();a.thumbnail((215,390));canvas.paste(a,(12+(215-a.width)//2,36+(390-a.height)))
 for j in [1,2]:
  bg=Image.new('RGBA',(220,390),'#0B2E45')
  if j==1:
   bd=ImageDraw.Draw(bg)
   for yy in range(0,390,12):
    for xx in range(0,220,12):bd.rectangle((xx,yy,xx+11,yy+11),fill='#CFD8DB' if (xx//12+yy//12)%2 else '#EDF1F2')
  a=rgba.copy();a.thumbnail((215,380));bg.alpha_composite(a,((220-a.width)//2,390-a.height));canvas.paste(bg.convert('RGB'),(j*240+10,36))
 canvas.save(q/f'awards-cut/awards-{i:02}-comparison.png')
assert max(heights)/min(heights)<=1.35
# Tight but uncrowded variable-width row; all image bottoms share y=750.
items=list(reversed(assets));cursor=0
for a in items:a['x']=round(cursor,4);cursor+=a['display_width']+24
total=cursor-24;travel=max(0,total-1100);duration=5.1;hold_start=1.35;hold_end=.9;moving=duration-hold_start-hold_end
assert travel/moving < 988/4.9
motion={'window_left':700,'window_width':1100,'baseline_y':750,'row_width':total,'travel':travel,'duration':duration,'entry_wipe_s':.45,'initial_hold_s':hold_start,'final_hold_s':hold_end,'motion_speed_px_s':travel/moving,'previous_speed_px_s':988/4.9,'height_ratio':max(heights)/min(heights)}
(q/'awards-layout.json').write_text(json.dumps({'items':items,'motion':motion},ensure_ascii=False,indent=2)+'\n')
(R/'src/config/awards-stage2.json').write_text(json.dumps({'items':items,'motion':motion},ensure_ascii=False,indent=2)+'\n')
# Use 25 of 27 for a complete 5x5 rectangle. Selection is a layout judgment,
# not an unverified claim about company popularity or relationship status.
keep=[i for i in range(1,28) if i not in [21,27]]
(q/'logo-selection.md').write_text('''# 25格供应商网格选择

保留：01–20、22–26，按原PDF顺序排列5×5，原色字标保留。银行标志单列，不混入供应商25格。

剔除仅限本次画面：21 seasonalife（细线环标／较大留白，小格内辨识较弱）；27 Bupa（源图以较小实色方块为主，小字缩到网格后辨识较弱）。原始文件保留，未删除、未据此断言公司冷门、合作终止或业务质量；这是画面取舍，未采用未经核实的市场排名。

100亿镜只标供应商；15亿镜供应商整体左移120px、整体透明度45%，标题切换为下方银行服务网络，避免双标题。
''')
# Latest user feedback overrides the old 0.18-0.30s spacing: all 25 suppliers
# must be fully lit BEFORE the premium -> commission transition, with a hold.
original=json.loads((R/'src/config/beats-v11.json').read_text())['onsets_s'];fps=30
def snap_frame(target):
 nearest=min(original,key=lambda n:abs(n-target))
 return math.floor((nearest if abs(nearest-target)<.18 else target)*fps+.5)
scene_start=snap_frame(14.35);scene_end=snap_frame(17.5);fade_s=.18
first=scene_start+1;full_hold_frames=25;last=scene_end-full_hold_frames-math.ceil(fade_s*fps)
schedule=[{'time':round((first+round(i*(last-first)/24))/fps,8),'frame':first+round(i*(last-first)/24),'kind':'accelerated scene-bounded timing'} for i in range(25)]
assert schedule[-1]['frame']+math.ceil(fade_s*fps)<=scene_end-full_hold_frames
spec={'keep_ids':keep,'light_schedule':schedule,'rows':5,'cols':5,'grid_left':1040,'grid_top':280,'cell_w':142,'cell_h':80,'gap_x':11,'gap_y':12,'commission_shift':120,'commission_opacity':.45,'lighting_revision':{'id':'stage2-logo-r01','scene_start_frame':scene_start,'next_scene_frame':scene_end,'fade_seconds':fade_s,'all_lit_frame':last+math.ceil(fade_s*fps),'full_hold_frames':full_hold_frames,'reason':'User requires every supplier lit before the next scene; latest instruction supersedes old interval constraint.'}}
(R/'src/config/logos-stage2.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n');(q/'logo-lighting.json').write_text(json.dumps({'spec':spec,'notes':'Accelerated scene-bounded sequence per latest user feedback; no claim of per-logo drum-beat alignment.'},ensure_ascii=False,indent=2)+'\n')
baseline={}
for p in list((R/'src').rglob('*'))+[R/'public/brand/closing-r01/slogan-brush.svg',R/'out/BOI-HK_史詩形象片_v11.mp4',R/'out/BOI-HK_史詩形象片_v12_第一階段試片.mp4',R/'public/music/v12/review-mix.wav']:
 if p.is_file() and p.name not in ['Root.tsx','awards-stage2.json','logos-stage2.json']:baseline[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
(q/'baseline.json').write_text(json.dumps(baseline,ensure_ascii=False,indent=2)+'\n');shutil.copy2(R/'src/Root.tsx',q/'Root-before.tsx')
print('8 PNGs, protected highlights, 25-logo schedule ready; awards speed',round(travel/moving,2),'vs',round(988/4.9,2))
print('All 25 fully lit at frame',last+math.ceil(fade_s*fps),'before next scene',scene_end)
