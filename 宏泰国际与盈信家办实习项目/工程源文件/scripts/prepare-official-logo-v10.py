"""Extract original, visible SVG primitives for animation. No tracing or redrawing.
Uses the existing fontTools BoundsPen solely to locate each original path.
"""
from pathlib import Path
from fontTools.svgLib.path import parse_path
from fontTools.pens.boundsPen import BoundsPen
import xml.etree.ElementTree as E,json,re,math,hashlib,shutil
R=Path(__file__).resolve().parents[1];Q=R/'qa/v10';Q.mkdir(parents=True,exist_ok=True)
A=R/'public/brand/v10';A.mkdir(parents=True,exist_ok=True)
src=Path('/Users/linwenbin/Desktop/宏泰.svg');retained=A/'宏泰.svg'
if retained.exists():
 if retained.read_bytes()!=src.read_bytes():raise ValueError('Source changed; use a new version instead of replacing the retained SVG')
else:shutil.copy2(src,retained)
text=src.read_text();inner=text[text.index('>',text.index('<svg'))+1:text.rindex('</svg>')]
(R/'src/assets/official-source-v10.json').write_text(json.dumps({'inner':inner},ensure_ascii=False,separators=(',',':')))
r=E.parse(src).getroot();tree=r[1][2];words=r[1][3]
def bound(e):
 boxes=[]
 for n in e.iter():
  typ=n.tag.split('}')[-1];d=None
  if typ=='path':d=n.get('d')
  if typ=='polygon':
   a=re.findall(r'[-+]?(?:\d*\.\d+|\d+)',n.get('points'));d='M'+'L'.join(' '.join(p)for p in zip(a[::2],a[1::2]))+'Z'
  if typ=='rect':
   x,y,w,h=[float(n.get(k,'0'))for k in ('x','y','width','height')];boxes.append((x,y,x+w,y+h))
  if d:
   p=BoundsPen(None);parse_path(d,p);boxes.append(p.bounds)
 return [min(b[0]for b in boxes),min(b[1]for b in boxes),max(b[2]for b in boxes),max(b[3]for b in boxes)]
colors={'st0':'#007bc7','st1':'#0093d0','st8':'#0093d0','st9':'#004098','st3':'#004098','st7':'#0051a4','st4':'url(#linear-gradient1)'}
def node(e):
 t=e.tag.split('}')[-1];attrs={k:v for k,v in e.attrib.items()if k not in ('class','id','data-name')};c=e.get('class')
 if c:attrs.update(fill=colors[c],fillRule='evenodd'if c in ['st0','st1','st3','st4','st7']else'nonzero')
 return {'tag':t,'attrs':attrs,'children':[node(x)for x in e]}
leaves=[];cx=56.85;cy=56.05;radii=[16.6,25.3,32.8,38.5,42.6,46]
for i,l in enumerate(tree[1:-1],1):
 b=bound(l);x=(b[0]+b[2])/2;y=(b[1]+b[3])/2;rad=math.hypot(x-cx,y-cy);deg=math.degrees(math.atan2(cy-y,x-cx))
 ring=5 if 2<=i<=37 else min(range(5),key=lambda k:abs(rad-radii[k]))
 leaves.append({'sourceIndex':i,'node':node(l),'bounds':b,'x':x,'y':y,'r':rad,'deg':deg,'ring':ring})
old=json.loads((R/'src/assets/tree.json').read_text());windows=[]
for i in range(6):
 d=[3+i*.55+abs(90-l['deg'])/110*.45 for l in old['LEAF_CONTOURS']if l['ring']==i];windows.append([min(d),max(d)])
for ring in range(6):
 a=[l for l in leaves if l['ring']==ring];angles=[abs(90-l['deg'])for l in a];lo,hi=min(angles),max(angles)
 for l in a:
  p=(abs(90-l['deg'])-lo)/(hi-lo)if hi>lo else 0
  l['delay']=windows[ring][0]+p*(windows[ring][1]-windows[ring][0])
 print('ring',ring+1,'count',len(a),'radii',round(min(l['r']for l in a),2),round(max(l['r']for l in a),2))
cn=sorted([{'node':node(c),'bounds':bound(c)}for c in words[:4]],key=lambda c:c['bounds'][0]);en=[node(c)for c in words[4:]]
tb=bound(tree);wb=bound(words);union=[min(tb[0],wb[0]),min(tb[1],wb[1]),max(tb[2],wb[2]),max(tb[3],wb[3])]
out={'sourceSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'sourceViewBox':r.get('viewBox'),
 'sourceGroupIndices':[2,3],'bounds':union,'treeBounds':tb,'wordBounds':wb,'trunk':node(tree[0]),'base':node(tree[-1]),
 'leaves':leaves,'chinese':cn,'english':en,'ringWindows':windows,
 'ringCounts':[sum(l['ring']==i for l in leaves)for i in range(6)],
 'visiblePrimitives':len(list(tree))+sum(1 for x in words.iter()if x.tag.split('}')[-1]in('path','polygon','rect'))}
(R/'src/assets/official-logo-v10.json').write_text(json.dumps(out,ensure_ascii=False,separators=(',',':')))
(Q/'source-structure.json').write_text(json.dumps({k:v for k,v in out.items()if k not in('leaves','chinese','english','trunk','base')},ensure_ascii=False,indent=2))
print('asset',len(leaves),'leaves',len(cn),'Chinese glyph groups',len(en),'English glyphs','bounds',union)
