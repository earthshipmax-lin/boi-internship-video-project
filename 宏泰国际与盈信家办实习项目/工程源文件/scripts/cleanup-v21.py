from pathlib import Path
import json,hashlib,subprocess,shutil
R=Path(__file__).resolve().parents[2];V=R/'video';A=V/'qa/archive-v21-20261028'
assert json.load(open(A/'restore-verification.json'))['allFiveSHA256Match']
release=json.loads(subprocess.check_output(['gh','api','repos/earthshipmax-lin/boi-internship-video-project/releases/tags/v21-final-2026-10-28']));assert not release['draft'];ex=json.load(open(A/'assets.json'));remote={x['name']:x for x in release['assets']};assert all(remote[x['name']]['digest']=='sha256:'+x['sha256'] for x in ex)
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
manifest=json.load(open(A/'manifest.json'));rows=[]
for row in manifest:
 p=R/row['path']
 if p.suffix.lower() not in ['.mp4','.wav','.mp3','.png','.jpg','.jpeg','.zip'] and p.name!='scan-v20':continue
 assert p.is_file() and sha(p)==row['sha256'],p
 rows.append(row)
# Restored old audio had already been backed up in the original release and this run restored it with matching SHA.
for row in json.load(open(V/'qa/v20/restored.json')):
 p=V/row['path'];assert p.is_file() and sha(p)==row['sha256'];rows.append({'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':row['sha256'],'backup':'project-archive-2026-10-27'})
# Deduplicate and delete individually only after every hash passes.
rows=list({r['path']:r for r in rows}.values());report={'date':'2026-10-28','release':release['html_url'],'deletedMediaFiles':rows,'deletedMediaBytes':sum(r['bytes'] for r in rows),'rebuildableDependenciesBytes':0,'transferAndRedownloadBytes':0}
(A/'cleanup-plan.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
for row in rows:(R/row['path']).unlink()
# No active process is allowed to depend on this project's reinstallable node_modules.
node=V/'node_modules';ps=subprocess.check_output(['ps','-axo','command']).decode();active=[x for x in ps.splitlines() if str(node) in x]
if node.exists() and not active:
 report['rebuildableDependenciesBytes']=sum(p.stat().st_size for p in node.rglob('*') if p.is_file() and not p.is_symlink());shutil.rmtree(node)
for name in ['transfer','download-check']:
 p=A/name
 if p.exists():report['transferAndRedownloadBytes']+=sum(x.stat().st_size for x in p.rglob('*') if x.is_file());shutil.rmtree(p)
(A/'cleanup-complete.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='deletedMediaFiles'},ensure_ascii=False,indent=2))
