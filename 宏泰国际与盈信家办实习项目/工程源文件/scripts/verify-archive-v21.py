from pathlib import Path
import subprocess,json,time,hashlib,zipfile
R=Path(__file__).resolve().parents[2];A=R/'video/qa/archive-v21-20261028';repo='earthshipmax-lin/boi-internship-video-project';tag='v21-final-2026-10-28';expected=json.load(open(A/'assets.json'))
while True:
 try:r=json.loads(subprocess.check_output(['gh','api',f'repos/{repo}/releases/tags/{tag}'],stderr=subprocess.DEVNULL))
 except subprocess.CalledProcessError:time.sleep(5);continue
 assets={a['name']:a for a in r['assets']}
 if all(x['name'] in assets and assets[x['name']]['state']=='uploaded' for x in expected):break
 time.sleep(5)
for x in expected:
 a=assets[x['name']];assert a['size']==x['bytes'] and a['digest']=='sha256:'+x['sha256'],(x,a)
(A/'remote-verification.json').write_text(json.dumps({'releaseId':r['id'],'assets':[{'name':x['name'],'bytes':x['bytes'],'sha256':x['sha256'],'assetId':assets[x['name']]['id']} for x in expected],'allServerDigestsMatch':True},indent=2))
D=A/'download-check';D.mkdir(exist_ok=True)
for x in expected:
 p=D/x['name'];subprocess.run(['gh','release','download',tag,'--repo',repo,'--pattern',x['name'],'--dir',str(D)],check=True);assert p.stat().st_size==x['bytes'];assert hashlib.file_digest(p.open('rb'),'sha256').hexdigest()==x['sha256']
 if p.suffix=='.zip':
  with zipfile.ZipFile(p) as z:
   assert z.testzip() is None
   if p.name=='BOI-v20-v21-work-archive.zip':
    manifest=json.loads(z.read('_manifest.json'))
    for row in manifest:assert hashlib.sha256(z.read(row['path'])).hexdigest()==row['sha256']
   else:
    hashes=json.loads(z.read('SHA256.json'))
    for n,h in hashes.items():assert hashlib.sha256(z.read(n)).hexdigest()==h
 else:subprocess.run(['ffmpeg','-v','error','-i',str(p),'-f','null','-'],check=True)
 print('RESTORE VERIFIED',x['name'],flush=True)
(A/'restore-verification.json').write_text(json.dumps({'allFiveAssetsDownloaded':True,'allFiveSHA256Match':True,'allThreeFilmsDecoded':True,'bothZipCRCsPass':True,'archiveFilesIndividuallyVerified':len(manifest),'date':'2026-10-28'},indent=2))
subprocess.run(['gh','release','edit',tag,'--repo',repo,'--draft=false','--latest'],check=True)
print('PUBLISHED AND RESTORED',flush=True)
