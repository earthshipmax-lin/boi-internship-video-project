"""Keep more native portrait pixels for the user-requested 1.04 focus animation."""
from pathlib import Path
from PIL import Image,ImageEnhance
import json,hashlib
R=Path(__file__).resolve().parents[1];Q=R/'qa/us-v1-60s-v5';out=R/'public/portraits/us-v5';out.mkdir(exist_ok=True)
rows=[]
for p in json.loads((R/'src/config/us-team-v1.json').read_text()):
 rgb=Image.open(R/'qa/us-v1/source'/p['sourceImage']).convert('RGB');mask=Image.open(R/'qa/us-v1/source'/p['smask']).convert('L');rgba=rgb.convert('RGBA');rgba.putalpha(mask)
 bg=Image.new('RGBA',rgb.size,'#e9e5df');bg.alpha_composite(rgba);im=bg.convert('RGB')
 crop=im.resize((round(p['cropSize'][0]),p['nativeSize'][1]),Image.Resampling.LANCZOS,box=tuple(p['cropBox']))
 toned=ImageEnhance.Color(crop).enhance(.48);toned=Image.blend(toned,Image.new('RGB',crop.size,'#24211f'),.07);toned=Image.blend(toned,Image.new('RGB',crop.size,'#e9e5df'),.045)
 dest=out/(p['slug']+'.png');toned.save(dest)
 rows.append(dict(slug=p['slug'],size=list(toned.size),source=p['sourceImage'],sourcePage=19,baseScale=p['scale'],focusScale=p['scale']*1.04,sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),note='Preserve native crop and original grading; user-requested 1.04 scale exceeds source sampling slightly only for Vivian (1.032624). No AI detail reconstruction.'))
(Q/'source/portrait-scales.json').write_text(json.dumps(rows,indent=2)+'\n');print('Native portrait focus scales',[(r['slug'],round(r['focusScale'],6)) for r in rows])
