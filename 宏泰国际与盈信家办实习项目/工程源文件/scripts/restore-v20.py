from pathlib import Path
import json,hashlib,zipfile,time
V=Path(__file__).resolve().parents[1];Q=V/'qa/v20';meta=V/'qa/remote-archive-20261027';manifest={x['path']:x for x in json.load(open(V/'实习经历/宏泰国际与盈信家办/待备份文件清单.json'))['files']};restored=[]
for i in [3,4]:
 name=f'boi-project-archive-part-{i:02}-of-10.zip';info=json.load(open(meta/(name+'.verified.json')));z=Q/'restore'/name
 while not z.exists() or z.stat().st_size!=info['bytes']:time.sleep(3)
 assert hashlib.file_digest(z.open('rb'),'sha256').hexdigest()==info['sha256']
 with zipfile.ZipFile(z) as arc:
  for n in arc.namelist():
   if n.startswith('public/music/hk-v15/') and n.endswith('.wav') or n in ['public/music/hk-v19/cn-master.wav','public/music/hk-v19/cn-voice.wav']:
    data=arc.read(n);assert hashlib.sha256(data).hexdigest()==manifest[n]['sha256'];p=V/n;p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():assert hashlib.sha256(p.read_bytes()).hexdigest()==manifest[n]['sha256']
    else:p.write_bytes(data)
    restored.append({'path':n,'sha256':manifest[n]['sha256']});print('RESTORED',n,flush=True)
 z.unlink()
(Q/'restored.json').write_text(json.dumps(restored,indent=2))
