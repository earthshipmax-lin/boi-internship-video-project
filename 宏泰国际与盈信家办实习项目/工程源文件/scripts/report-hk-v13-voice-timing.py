from pathlib import Path
import json
V=Path(__file__).resolve().parents[1];Q=V/'qa/v13/people/voice-production-r01'
m=json.loads((Q/'measurements.json').read_text())['records'];rows=[]
for r in m:
 if not r['id'].startswith('caption-'):continue
 window=r['originalEnd']-r['originalStart'];activity=r['diagnostic_activity_minus45dB']
 rows.append({'locale':r['locale'],'id':r['id'],'text':r['text'],'start':r['originalStart'],'end':r['originalEnd'],'window':round(window,3),'fullSourceDuration':r['duration'],'overWindow':round(max(0,r['duration']-window),6),'diagnosticActiveDuration':None if activity['start'] is None else round(activity['end']-activity['start'],6),'diagnosticNote':'-45dB threshold only; do not use to crop audio.'})
report={'status':'measurement_only_no_timing_edits','records':rows,'overruns':[r for r in rows if r['overWindow']>1/48000],'rule':'Prompt13 section4.5: report overruns before handling; no acceleration or speech crop.'}
(Q/'timing-overruns.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'measured_original_cues':len(rows),'overruns':len(report['overruns']),'largest':sorted(report['overruns'],key=lambda r:r['overWindow'],reverse=True)[:3]},ensure_ascii=False))
