"""Independent static SVG reference calculated from approved source geometry.
Does not navigate to or control the original file:// browser tab.
"""
from pathlib import Path
import re,json,xml.etree.ElementTree as E
root=Path(__file__).resolve().parents[2];out=root/'video/public/reference';out.mkdir(exist_ok=True)
source=(root/'prototype/logo-reveal/index.html').read_text()
leaves=json.loads(re.search(r'const LEAF_CONTOURS = (.*);',source)[1]);leaves=sorted(leaves,key=lambda p:p['ring'])
ns='http://www.w3.org/2000/svg';E.register_namespace('',ns)
def ease(t):return 1-(1-max(0,min(1,t)))**4
references={}
for frame in [114,150,252,285]:
 now=frame/30
 full=E.Element('{'+ns+'}svg',{'width':'1920','height':'1080','viewBox':'0 0 1920 1080'})
 E.SubElement(full,'{'+ns+'}rect',{'width':'1920','height':'1080','fill':'oklch(97% 0.01 80)'})
 tree=E.parse(root/'prototype/logo-reveal/boi_tree_rebuild_v2.svg').getroot();tree.set('x','430');tree.set('y','348')
 base=tree.find('.//*[@id="base"]');pb=ease((now-1.2)/.9);mid=38.1+94.87/2;base.set('transform',f'translate({mid} 0) scale({pb} 1) translate({-mid} 0)')
 trunk=tree.find('.//*[@id="trunk"]');pt=ease((now-2)/1.2);trunk.set('style',f'clip-path:inset({(1-pt)*100}% 0 0 0)')
 nodes=[n for n in tree.iter() if n.get('class')=='leaf']
 for n,l in zip(nodes,leaves):
  delay=3+l['ring']*.55+abs(90-l['deg'])/110*.45;p=ease((now-delay)/.5);n.set('opacity',f'{p:.3f}');n.set('transform',f'scale({.2+.8*p:.5f})')
 full.append(tree)
 wm=E.parse(root/'prototype/logo-reveal/wordmark-clean.svg').getroot();wm.set('viewBox','150 18 270 92');wm.set('x','890');wm.set('y',str(540-(int(600*92/270*64)/64)/2));wm.set('width','600');wm.set('height',str(int(600*92/270*64)/64));pw=ease((now-7.4)/1);wm.set('opacity',str(pw))
 for id,left,right in [('name-area',178.27,352.04),('english-area',160.05,375.68)]:
  rect=wm.find('.//*[@id="'+id+'"]/{'+ns+'}rect');w=(right-left+1)*pw;rect.set('x',f'{(left+right-w)/2:.4f}');rect.set('width',f'{w:.4f}')
 full.append(wm);E.ElementTree(full).write(out/f'prototype-f{frame}.svg',encoding='unicode')

 # An HTML/SVG layout reference avoids external-image edge rasterization differences.
 for n in [tree,wm]:
  n.attrib.pop('x',None);n.attrib.pop('y',None)
 tree.set('style','overflow:visible;flex-shrink:0')
 wm.set('height',str(600*92/270));wm.set('style','display:block;flex-shrink:0')
 references[frame]='<div style="position:absolute;inset:0;background:oklch(97% 0.01 80)"><div style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);display:flex;align-items:center;gap:40px">'+E.tostring(tree,encoding='unicode')+E.tostring(wm,encoding='unicode')+'</div></div>'
(root/'video/src/assets/prototype-reference.json').write_text(json.dumps(references))

print('Built four source-derived layout references')
