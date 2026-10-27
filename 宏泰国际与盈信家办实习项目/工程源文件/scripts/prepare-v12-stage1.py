from pathlib import Path
from PIL import Image,ImageDraw
import json,math,struct,hashlib,shutil
R=Path(__file__).resolve().parents[1];q=R/'qa/v12';dest=R/'public/stills/v12';dest.mkdir(parents=True,exist_ok=True)
manifest=[]
def page(n):return Image.open(next((R/'qa/v11-ref/hi').glob(f'pg{n}-*'))).convert('RGB')
def crop(n,box,name,role,display=None):
 im=page(n);scale=im.width/1440;b=tuple(round(v*scale) for v in box);out=im.crop(b)
 outdir=R/'archive/v12/image-inventory' if 'inventory only' in role else dest;outdir.mkdir(parents=True,exist_ok=True)
 out.save(outdir/name,quality=97)
 file_ref=str((outdir/name).relative_to(R)) if 'inventory only' in role else f'stills/v12/{name}'
 manifest.append({'file':file_ref,'page':n,'crop_pdf_points':box,'crop_render_pixels':b,'pixels':list(out.size),'role':role,'planned_display':display,'quality':'review in actual rendered size; no invented effective DPI'})
 return file_ref
xs=[109,286,463,640,817,994,1172];ys=[236,368,499,631]
logos=[]
for row in range(4):
 for col in range(7 if row<3 else 6):
  # Crop inside the source table rules, retain the original logo colours.
  name=f'provider-hk-{len(logos)+1:02}.jpg';logos.append(crop(6,[xs[col]+4,ys[row]+4,xs[col]+162,ys[row]+117],name,'Hong Kong insurance product provider', [142,88]))
# Keep banks distinct from product providers, and do not extract p19 portraits.
banks=[crop(20,[164,190,538,272],'bank-minsheng.jpg','bank', [300,75]),crop(20,[883,184,1291,304],'bank-shanghai.jpg','bank',[300,90])]
awards=[]
boxes=[[89,155,183,410],[299,156,389,414],[486,167,608,414],[704,166,825,418],[49,435,209,646],[217,441,367,646],[380,435,672,646],[685,435,841,646]]
for i,b in enumerate(boxes):awards.append(crop(5,b,f'awards-{i+1:02}.jpg','award / certificate',[166,250]))
# Inventory useful US logos now; only HK providers and banks are active in Stage 1.
us=[]
for i,b in enumerate([[670,234,784,291],[804,234,919,291],[940,234,1054,291],[1075,234,1190,291],[1210,234,1325,291],[670,321,784,378],[670,408,784,465],[805,408,919,465],[940,408,1054,465],[1075,408,1190,465]]):
 us.append(crop(12,b,f'provider-us-{i+1:02}.jpg','US product provider; inventory only',None))
(q/'photos-manifest.json').write_text(json.dumps({'source':'qa/v11-ref/intro.pdf','active_stage':'P1 + P2','excluded':'p19 is portraits and biographies, not logos; no extraction','assets':manifest,'inactive_inventory':us},ensure_ascii=False,indent=2)+'\n')
(R/'src/config/photos-v12.ts').write_text('// Stage 1: common left-to-right reveal; no random motion. Chronology is not invented.\n// Spatial ordering HK → SZ → NY → Singapore (planned); award/provider/bank roles stay distinct.\nexport const providerLogos='+json.dumps(logos,ensure_ascii=False)+' as const;\nexport const bankLogos='+json.dumps(banks,ensure_ascii=False)+' as const;\nexport const awardPhotos='+json.dumps(awards,ensure_ascii=False)+' as const;\n')
# Read Natural Earth Polygon shapefile with Python standard library (no new dependency).
data=(q/'map-source/ne_110m_land.shp').read_bytes();pos=100;rings=[]
while pos<len(data):
 _,length=struct.unpack('>2i',data[pos:pos+8]);raw=data[pos+8:pos+8+length*2];pos+=8+length*2
 if struct.unpack('<i',raw[:4])[0]!=5:continue
 parts,pts=struct.unpack('<2i',raw[36:44]);ix=list(struct.unpack('<'+'i'*parts,raw[44:44+parts*4]))+[pts];coords=struct.unpack('<'+'d'*(pts*2),raw[44+parts*4:44+parts*4+pts*16]);points=list(zip(coords[::2],coords[1::2]))
 for a,b in zip(ix,ix[1:]):rings.append(points[a:b])
def clip(poly,axis,bound,greater):
 if not poly:return []
 out=[];prev=poly[-1];inside=lambda p:p[axis]>=bound if greater else p[axis]<=bound
 for cur in poly:
  if inside(cur)!=inside(prev):
   k=(bound-prev[axis])/(cur[axis]-prev[axis]);out.append(tuple(prev[j]+k*(cur[j]-prev[j]) for j in [0,1]))
  if inside(cur):out.append(cur)
  prev=cur
 return out
def project(lon,lat):return [round(140+(lon+40)/360*1640,3),round(320+(80-lat)*4.4,3)]
paths=[]
for ring in rings:
 for offset in [0,360]:
  p=[(x+offset,y) for x,y in ring]
  for axis,bound,g in [(0,-40,True),(0,320,False),(1,-50,True),(1,85,False)]:p=clip(p,axis,bound,g)
  if len(p)>2:paths.append('M'+' L'.join(f'{x:.2f} {y:.2f}' for x,y in [project(*z) for z in p])+'Z')
cities={'香港':[114.1694,22.3193],'深圳':[114.0579,22.5431],'紐約':[-74.006,40.7128],'新加坡':[103.8198,1.3521]}
def gc(a,b):
 def vec(ll):
  lon,lat=map(math.radians,ll);return [math.cos(lat)*math.cos(lon),math.cos(lat)*math.sin(lon),math.sin(lat)]
 u,v=vec(a),vec(b);theta=math.acos(max(-1,min(1,sum(x*y for x,y in zip(u,v)))));out=[]
 for i in range(101):
  t=i/100;s=math.sin(theta) or 1;w=[math.sin((1-t)*theta)/s*u[j]+math.sin(t*theta)/s*v[j] for j in range(3)];lon=math.degrees(math.atan2(w[1],w[0]));lat=math.degrees(math.atan2(w[2],math.hypot(w[0],w[1])));out.append(project(lon+360 if lon<-40 else lon,lat))
 return out
routes={name:gc(cities['香港'],coords) for name,coords in cities.items() if name!='香港'}
onsets={'香港':31.28,'深圳':32.06,'紐約':32.42,'新加坡':33.50}
out={'land_paths':paths,'cities':{n:{'lon':ll[0],'lat':ll[1],'xy':project(ll[0]+360 if ll[0]<-40 else ll[0],ll[1]),'cue':onsets[n]} for n,ll in cities.items()},'routes':routes,'projection':{'type':'equirectangular affine','longitude_range':[-40,320],'latitude_range':[-50,85],'x0':140,'width':1640,'y_at_80':320,'pixels_per_latitude_degree':4.4},'map_source':'Natural Earth ne_110m_land, land only, no borders','coordinate_scope':'city reference points, not office GPS or navigation','timing_method':'v11 reference-text per-character alignment; needs human listening confirmation'}
(R/'src/assets/world-v12.json').write_text(json.dumps(out,ensure_ascii=False,separators=(',',':'))+'\n');(q/'map-spec.json').write_text(json.dumps({k:v for k,v in out.items() if k not in ['land_paths','routes']},ensure_ascii=False,indent=2)+'\n')
(q/'map-source/PROVENANCE.md').write_text('Natural Earth land polygons: https://www.naturalearthdata.com/downloads/110m-physical-vectors/110m-land/\nDownload: https://naciscdn.org/naturalearth/110m/physical/ne_110m_land.zip\nTerms: https://www.naturalearthdata.com/about/terms-of-use/ (public domain).\nLand only, no boundaries, generated locally from geographic coordinates. Not an Internet stock image. City reference points use WGS84 degrees and are not exact office positions.\n')
base={}
for p in list((R/'src').rglob('*'))+[R/'out/BOI-HK_史詩形象片_v11.mp4',R/'out/BOI-HK_史詩形象片_v11_片尾修訂r01.mp4',R/'public/music/v11/bgm-A.mp3']:
 if p.is_file() and p.name not in ['Root.tsx','world-v12.json','photos-v12.ts'] and not any(x in p.name for x in ['V12','v12']):base[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
(q/'baseline.json').write_text(json.dumps(base,ensure_ascii=False,indent=2)+'\n');shutil.copy2(R/'src/Root.tsx',q/'Root-before.tsx')
print('Prepared',len(logos),'provider logos,',len(banks),'banks,',len(awards),'award crops;',len(paths),'land paths')
