from pathlib import Path
import subprocess,json,math
import numpy as np
V=Path(__file__).resolve().parents[1];Q=V/'qa/v14';report={}
for loc in ['yue','en','cn']:
 p=V/f'src/config/timeline-v14-{loc}.json';t=json.loads(p.read_text());backup=Q/f'{loc}-timeline-before-caption-boundary.json'
 if backup.exists():t=json.loads(backup.read_text())
 else:backup.write_text(json.dumps(t,ensure_ascii=False,indent=2))
 for c in t['cues']:c['startFrame']=int(c['startFrame']);c['endFrame']=int(c['endFrame'])
 a=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(V/f'public/music/hk-v14/{loc}-voice.wav'),'-f','f32le','-ar','48000','-ac','2','-']),dtype='<f4').reshape(-1,2);n=t['durationInFrames'];peak=np.max(np.abs(a[:n*1600]).reshape(n,1600,2),axis=(1,2));active=peak>10**(-42/20)
 changes=[]
 for i,c in enumerate(t['cues']):
  # The earlier source cue table can lag the actual waveform. Search all of the
  # measured phrase gap, instead of clipping the search to +/-120ms of that table.
  left=t['cues'][i-1]['endFrame'] if i else 0;right=c['startFrame']
  hits=np.where(active[max(0,left):right])[0]
  if len(hits):
   new=max(left,max(0,left)+int(hits[0])-1);changes.append({'id':c['id'],'oldStart':c['startFrame'],'newStart':new,'advanceSeconds':(c['startFrame']-new)/30});c['startFrame']=new
 for i,c in enumerate(t['cues']):
  right=t['cues'][i+1]['startFrame'] if i+1<len(t['cues']) else n
  hits=np.where(active[c['endFrame']:right])[0]
  if len(hits):c['endFrame']=min(right,c['endFrame']+int(hits[-1])+2)
 for a,b in zip(t['cues'],t['cues'][1:]):a['endFrame']=min(a['endFrame'],b['startFrame'])
 p.write_text(json.dumps(t,ensure_ascii=False,indent=2)+'\n');report[loc]=changes
(Q/'caption-boundary-corrections.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print({l:len(v) for l,v in report.items()})
