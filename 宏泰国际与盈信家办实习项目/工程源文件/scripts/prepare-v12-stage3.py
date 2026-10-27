from pathlib import Path
from PIL import Image,ImageDraw,ImageOps
import hashlib,json
import numpy as np

R=Path(__file__).resolve().parents[1];Q=R/'qa/v12/stage3';S=Q/'native-source'
for p in [Q/'native-cut',R/'public/stills/v12/cut',R/'public/stills/v12/docs']:
    p.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
items=[]
for i,name in enumerate([16,6,8,10]):
    source=S/f'a-{name:03}.png';im=Image.open(source).convert('RGB')
    assert np.array_equal(np.asarray(im),np.asarray(Image.open(R/f'qa/v11-ref/awards-native/a-{name:03}.png').convert('RGB')))
    mask=Image.open(S/f'a-{name+1:03}.png').convert('L');rgb=np.asarray(im)
    # Threshold only the external black. The PDF's original soft mask protects
    # dark lettering/bases and metallic highlights from brightness-key damage.
    alpha=np.array(mask);dark=(rgb.astype(float)@np.array([.2126,.7152,.0722]))<8
    alpha[(alpha==0)&dark]=0
    bbox=Image.fromarray(alpha).getbbox();assert bbox
    rgba=im.convert('RGBA');rgba.putalpha(Image.fromarray(alpha));cut=rgba.crop(bbox)
    path=R/f'public/stills/v12/cut/native-a{name:03}.png';assert not path.exists();cut.save(path)
    scale=min(1,560/cut.height);h=cut.height*scale;w=cut.width*scale
    items.append({'id':f'native-a{name:03}','file':str(path.relative_to(R/'public')),'source':str(source.relative_to(R)),'source_sha256':sha(source),'category':'trophy','source_pixels':list(im.size),'crop':list(bbox),'output_pixels':list(cut.size),'scale':scale,'display_width':w,'display_height':h,'baseline':1030,'alpha_source':f'a-{name+1:03}.png','protected_source_rgb':True})

# Rectangles include each complete outer frame and very little surrounding wall.
crops={4:(158,32,728,1114),5:(136,34,784,1188),12:(0,0,313,455),13:(117,180,606,833),14:(238,338,650,912),15:(132,438,1144,1208)}
for name in [4,5,12,13,14,15]:
    ext='jpg' if name in [4,5,12] else 'png';source=S/f'a-{name:03}.{ext}';im=Image.open(source).convert('RGB')
    box=crops[name];crop=im.crop(box);border=max(1,round(min(crop.size)*.02));cut=ImageOps.expand(crop,border=border,fill='white')
    path=R/f'public/stills/v12/docs/native-a{name:03}.png';assert not path.exists();cut.save(path)
    scale=240/cut.height;assert scale<=1
    items.append({'id':f'native-a{name:03}','file':str(path.relative_to(R/'public')),'source':str(source.relative_to(R)),'source_sha256':sha(source),'category':'document','source_pixels':list(im.size),'crop':list(box),'border_pixels':border,'output_pixels':list(cut.size),'scale':scale,'display_width':cut.width*scale,'display_height':240,'top':330,'orientation_exception':name==15,'note':'Original landscape certificate kept complete; not cropped into a portrait or stretched.' if name==15 else 'Complete document/frame retained with 2% white breathing space.'})

front=items[:4];back=items[4:]
for row,gap in [(front,40),(back,36)]:
    total=sum(a['display_width'] for a in row)+gap*(len(row)-1);x=(1920-total)/2
    for a in row:
        a['x']=x
        if a['category']=='trophy':a['top']=1030-a['display_height']
        x+=a['display_width']+gap
assert all(a['scale']<=1 for a in items)
spec={'items':items,'front_baseline':1030,'front_gap':40,'back_top':330,'back_height':240,'back_opacity':.72,'back_mist_opacity':.06,'entry_stagger_frames':5,'front_entry_seconds':.5,'back_delay_seconds':.25,'back_entry_seconds':.6,'rest_motion':'none','header_layout':'one line at y174 to avoid logo/subtitle overlap','caption_layout':'trust captions top-right at y278, clear of all ten assets'}
(R/'src/config/awards-stage3.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n')
(Q/'scale-table.json').write_text(json.dumps(items,ensure_ascii=False,indent=2)+'\n')
lines=['# Native asset scale table','','| Asset | Original | Crop/output | Display | Scale |','| --- | --- | --- | --- | --- |']
for a in items:
    lines.append(f"| {a['id']} | {a['source_pixels']} | {a['output_pixels']} | {a['display_width']:.1f} x {a['display_height']:.1f} | {a['scale']:.4f} |")
(Q/'scale-table.md').write_text('\n'.join(lines)+'\n')
sheet=Image.new('RGB',(1500,4*390),'#173446');draw=ImageDraw.Draw(sheet)
for k,a in enumerate(items):
    original=Image.open(R/a['source']).convert('RGBA');cut=Image.open(R/'public'/a['file']).convert('RGBA')
    board=Image.new('RGB',(900,560),'#173446');d=ImageDraw.Draw(board)
    for j,img in enumerate([original,cut,cut]):
        img.thumbnail((280,490));bg=Image.new('RGBA',(300,520),(235,235,235,255) if j==1 else (11,46,69,255));bg.alpha_composite(img,((300-img.width)//2,(520-img.height)//2));board.paste(bg.convert('RGB'),(j*300,28));d.text((j*300+12,8),['native source','alpha / white mount','navy composite'][j],fill='white')
    board.save(Q/f"native-cut/{a['id']}-comparison.jpg",quality=94)
    tile=board.resize((500,312));x=k%3*500;y=k//3*390;sheet.paste(tile,(x,y+30));draw.text((x+12,y+7),a['id'],fill='white')
sheet.save(Q/'native-cut/all-comparisons.jpg',quality=94)
caps=json.loads((R/'src/config/captions-v12.json').read_text())
for c in caps:
    if c['start']>=28.2:c['start']=round(c['start']+2.1,5);c['end']=round(c['end']+2.1,5)
(R/'src/config/captions-v12-stage3.json').write_text(json.dumps(caps,ensure_ascii=False,indent=2)+'\n')
print('Prepared 4 native transparent trophies + 6 intact documents; scale max',max(a['scale'] for a in items))
