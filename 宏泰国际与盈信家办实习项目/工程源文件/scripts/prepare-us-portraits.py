"""Extracted PDF originals; reuse embedded alpha, no new segmentation or face retouch."""
from PIL import Image,ImageEnhance,ImageOps,ImageDraw,ImageFont
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];q=R/'qa/us-v1';out=R/'public/portraits/us-v1';s=q/'source'
people=[('david-wang','David Wang',2,(335,382),'Formerly at WFG'),('lily-ku','Lily Ku',6,(430,425),'Formerly at New York Life / MassMutual'),('noah-cheung','Noah Cheung',8,(297,364),'Engineering background'),('catherine-luo','Catherine Luo',4,(320,398),'Formerly at Deutsche Bank / RBS'),('vivian-mau','Vivian Mau',14,(282,282),'Formerly at WFG / PFA'),('crystal-wan','Crystal Wan',12,(474,571),'Formerly at PFA')]
records=[];compare=Image.new('RGB',(6*248,640),'#e9e5df');d=ImageDraw.Draw(compare)
font=ImageFont.truetype(str(R/'public/fonts/Geist.ttf'),15)
for i,(slug,name,idx,size,former) in enumerate(people):
 rgb=Image.open(s/f'p19-{idx:03}.png').convert('RGB');mask=Image.open(s/f'p19-{idx+1:03}.png').convert('L');assert rgb.size==size==mask.size
 rgba=rgb.convert('RGBA');rgba.putalpha(mask);rgba.save(out/f'{slug}-original.png')
 # Retain all RGB background content; composite only existing embedded transparency.
 bg=Image.new('RGBA',size,'#e9e5df');bg.alpha_composite(rgba);original=bg.convert('RGB')
 w,h=size;cw=h*4/5;box=((w-cw)/2,0,(w+cw)/2,h);assert 224/cw<=1 and 280/h<=1
 crop=original.resize((224,280),Image.Resampling.LANCZOS,box=box)
 # Same restrained global treatment for every image. No localized or geometric face edits.
 toned=ImageEnhance.Color(crop).enhance(.48)
 toned=Image.blend(toned,Image.new('RGB',crop.size,'#24211f'),.07)
 toned=Image.blend(toned,Image.new('RGB',crop.size,'#e9e5df'),.045)
 crop.save(q/f'{slug}-before.png');toned.save(out/f'{slug}.png')
 compare.paste(crop,(i*248+12,32));compare.paste(toned,(i*248+12,344));d.text((i*248+12,8),name,fill='#24211f',font=font)
 records.append({'slug':slug,'name':name,'sourcePage':19,'sourceImage':f'p19-{idx:03}.png','smask':f'p19-{idx+1:03}.png','nativeSize':size,'cropBox':box,'cropSize':[cw,h],'outputSize':[224,280],'scale':280/h,'supportingLine':former,'formerEmployerStatus':'PDF-sourced translation; company review pending','sourceSha256':hashlib.sha256((s/f'p19-{idx:03}.png').read_bytes()).hexdigest(),'preparedSha256':hashlib.sha256((out/f'{slug}.png').read_bytes()).hexdigest()})
assert (s/'p19-008.png').read_bytes()==(s/'p19-010.png').read_bytes()
compare.save(q/'portraits-before-after.png');(q/'portraits.json').write_text(json.dumps(records,indent=2))
(R/'src/config/us-team-v1.json').write_text(json.dumps(records,indent=2))
(q/'scale-table.md').write_text('# Native-scale check\n\n224 x 280 at 1920 x 1080. No card scale animation.\n\n|Name|Native|4:5 crop|Render scale|\n|---|---|---|---|\n'+''.join(f"|{r['name']}|{r['nativeSize']}|{r['cropSize']}|{r['scale']:.6f}|\n" for r in records))
print('Six unique portraits prepared. Maximum scale',max(r['scale'] for r in records))
