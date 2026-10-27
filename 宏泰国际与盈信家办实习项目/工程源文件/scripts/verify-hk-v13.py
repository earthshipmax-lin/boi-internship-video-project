"""Verify completed renders and distinguish technical QA from user approval."""
from pathlib import Path
import subprocess,json,hashlib,sys,re
V=Path(__file__).resolve().parents[1];preview='--yue-preview' in sys.argv
Q=V/('qa/v13/full/yue-preview-r01' if preview else 'qa/v13/full/final-r01')
t=json.loads((V/('src/config/timeline-v13-preview.json' if preview else 'src/config/timeline-v13.json')).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
protected=json.loads((V/'qa/v13/people/baseline.json').read_text());changed=[p for p,h in protected.items() if not (V/p).exists() or sha(V/p)!=h]
assert not changed,changed
versions=[('yue','粵語')] if preview else [('yue','粵語'),('en','英文'),('zh-CN','簡中')]
results={};layout_failures=[]
for loc,label in versions:
 movie=V/f"out/BOI-HK_史詩形象片_v13_{label}_{'加長預覽_r01' if preview else '加長版'}.mp4"
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(movie)]))
 video=next(s for s in probe['streams'] if s['codec_type']=='video');audio=next(s for s in probe['streams'] if s['codec_type']=='audio')
 assert (video['width'],video['height'],video['avg_frame_rate'],int(video['nb_frames']))==(1920,1080,'30/1',t['durationInFrames'])
 assert audio['sample_rate']=='48000' and audio['channels']==2
 subprocess.run(['ffmpeg','-v','error','-i',str(movie),'-f','null','-'],check=True,capture_output=True)
 rows=json.loads((Q/f'{loc}-layout-audit.json').read_text())
 for row in rows:
  d=row['data'];items=d.get('designText',d.get('texts',[]))
  for x in items:
   if x.get('opacity',1)<.99:continue
   rect=x.get('glyphRect') or x.get('fontRect') or x['rect']
   if rect['x']<-.5 or rect['y']<-.5 or rect['x']+rect['width']>1920.5 or rect['y']+rect['height']>1080.5:layout_failures.append([loc,d.get('frame',d.get('sourceFrame')),x.get('id',x.get('role')),'canvas'])
   if x.get('scrollWidth') and x['scrollWidth']>x['clientWidth']+1:layout_failures.append([loc,d.get('frame',d.get('sourceFrame')),x.get('id',x.get('role')),'box'])
  if 'photoTotalWidth' in d:
   assert abs(d['photoTotalWidth']-1660)<=1
   for p in d['photos']:assert p['nativeScaleX']<=1.600001 and p['grayscale']==0
 results[loc]={'file':str(movie.relative_to(V)),'sha256':sha(movie),'durationVideo':float(video['duration']),'durationContainer':float(probe['format']['duration']),'frames':int(video['nb_frames']),'format':'H264/AAC 1920x1080 30fps stereo48k','decodeComplete':True,'layoutSampleRecords':len(rows)}
result={'status':'technical_preview_pending_subjective_review' if preview else 'technical_delivery_pending_subjective_review','results':results,'protectedFilesUnchanged':len(protected),'protectedChanges':changed,'layoutFailures':layout_failures,'limits':['No claim of company approval or complete human pronunciation review.','Native frame checks are not H264 pixel identity.','Container AAC padding can add approximately20ms beyond video duration.','Original audio sample preservation is checked before added voice and final mix processing; old AAC packet identity is not claimed.']}
(Q/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
if layout_failures and not preview:raise SystemExit(str(layout_failures))
print(json.dumps({'videos':len(results),'protectedUnchanged':len(protected),'layoutFailures':layout_failures},ensure_ascii=False))
