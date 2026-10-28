from pathlib import Path
import json,hashlib,zipfile,shutil
R=Path(__file__).resolve().parents[2];V=R/'video';A=V/'qa/archive-v21-20261028';A.mkdir(exist_ok=True);T=A/'transfer';T.mkdir(exist_ok=True)
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
files=set()
for base in [V/'qa/v20',V/'qa/v21',V/'public/music/hk-v20']:
 files.update(p for p in base.rglob('*') if p.is_file())
files.update(p for p in (V/'src').rglob('*') if p.is_file() and 'v2' in p.name.lower() and ('v20' in p.name.lower() or 'v21' in p.name.lower()))
files.update(p for p in (V/'scripts').iterdir() if p.is_file() and ('v20' in p.name or 'v21' in p.name))
files.update(p for p in (V/'out').iterdir() if p.is_file() and ('v20' in p.name or 'v21' in p.name))
files.update([V/'README.md',R/'CLAUDE_HANDOFF.md',V/'qa/v11/CURRENT_SELECTION.json',R/'CODEX_PROMPT_20_刪除人物段與時長重排.md'])
files.update(R.glob('BOI-v2*-*.zip'))
manifest=[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(files)]
(A/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
p=T/'BOI-v20-v21-work-archive.zip'
assert not p.exists()
with zipfile.ZipFile(p,'x',zipfile.ZIP_DEFLATED,compresslevel=4) as z:
 for row in manifest:z.write(R/row['path'],row['path'])
 z.writestr('_manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2))
with zipfile.ZipFile(p) as z:assert z.testzip() is None
for loc,d in json.load(open(V/'qa/v21/deliverables.json')).items():shutil.copyfile(V/d['file'],T/f'BOI-v21-{loc.upper()}.mp4')
shutil.copyfile(R/'BOI-v21-三语树生长统一版_20261028.zip',T/'BOI-v21-three-language-delivery.zip')
assets=[{'name':p.name,'bytes':p.stat().st_size,'sha256':sha(p)} for p in T.iterdir() if p.is_file()]
(A/'assets.json').write_text(json.dumps(assets,indent=2));print(json.dumps(assets,indent=2),flush=True)
