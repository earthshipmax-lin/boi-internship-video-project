from pathlib import Path
import json,re,math,struct
import numpy as np
from PIL import Image
V=Path(__file__).resolve().parents[1];q=V/'qa/v13/redesign';q.mkdir(exist_ok=True,parents=True)
s=(V/'src/config/logo-optical-v12.ts').read_text();logos=json.loads(s.split('export const logoOpticalV12 = ')[1].split(' as const')[0]);out=[]
for r in logos:
 im=Image.open(V/'public'/r['file']).convert('RGB').crop(tuple(r['ink']));a=np.array(im).astype(float);lum=.2126*a[:,:,0]+.7152*a[:,:,1]+.0722*a[:,:,2];alpha=np.clip((245-lum)/170,0,1);alpha[alpha<.06]=0
 rgba=np.empty((*alpha.shape,4),dtype=np.uint8);rgba[:,:,:3]=[244,238,226];rgba[:,:,3]=(alpha*255).astype('uint8');p=V/f"public/logos/mono/{r['id']}.png";Image.fromarray(rgba).save(p)
 w,h=im.size;scale=min(math.sqrt(6000/(w*h)),56/h,220/w);out.append({'id':r['id'],'file':f"logos/mono/{r['id']}.png",'width':w*scale,'height':h*scale,'source':r['file'],'boxArea':w*h*scale**2})
(V/'src/config/logos-mono-v13.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
world=json.loads((V/'src/assets/world-v12.json').read_text());world={k:world[k] for k in ['land_paths','projection','map_source']};(V/'src/assets/world-redesign-v13.json').write_text(json.dumps(world,separators=(',',':'))+'\n')
# Independently compare three source shoreline vertices against the rendered path coordinates.
source=next((V/'qa').rglob('ne_110m_land.shp'));data=source.read_bytes();pos=100;pts=[]
while pos<len(data):
 _,length=struct.unpack('>2i',data[pos:pos+8]);raw=data[pos+8:pos+8+length*2];pos+=8+length*2
 if struct.unpack('<i',raw[:4])[0]!=5:continue
 nparts,npts=struct.unpack('<2i',raw[36:44]);co=struct.unpack('<'+'d'*(npts*2),raw[44+nparts*4:44+nparts*4+npts*16]);pts+=list(zip(co[::2],co[1::2]))
xy=np.array([tuple(map(float,m)) for p in world['land_paths'] for m in re.findall(r'([\d.-]+) ([\d.-]+)',p)])
rows=[]
for name,lon,lat in [('Cape of Good Hope',18.5,-34.3),('Cape Comorin',77.5,8.1),('Long Island',-72.0,41.0)]:
 p=min(pts,key=lambda p:(p[0]-lon)**2+(p[1]-lat)**2);lo=p[0]+360 if p[0]<-40 else p[0];screen=np.array([140+(lo+40)/360*1640,320+(80-p[1])*4.4]);err=float(np.linalg.norm(xy-screen,axis=1).min());assert err<2;rows.append({'coast':name,'sourceVertex':p,'projected':screen.tolist(),'nearestLandVertexErrorPx':err})
(q/'asset-projection-check.json').write_text(json.dumps({'logos':out,'coastChecks':rows,'source':str(source.relative_to(V)),'legacyWorldUntouched':True,'newMapHasNoHandwrittenCityXY':True},ensure_ascii=False,indent=2)+'\n')
print('Prepared',len(out),'mono logos, projection checks:',rows)
