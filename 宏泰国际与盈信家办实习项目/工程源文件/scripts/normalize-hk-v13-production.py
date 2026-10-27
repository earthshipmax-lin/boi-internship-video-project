"""Normalize downloaded authorized clips without cropping, stretching or pitch shifts."""
from pathlib import Path
import hashlib,json,re,subprocess
import numpy as np
V=Path(__file__).resolve().parents[1];Q=V/'qa/v13/people/voice-production-r01';R=48000
base='aresample=48000,aformat=channel_layouts=stereo'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def measure(p,prefix=''):
 af=(prefix+',' if prefix else '')+'loudnorm=I=-16:TP=-1.2:LRA=11:print_format=json'
 r=subprocess.run(['ffmpeg','-v','info','-i',str(p),'-af',af,'-f','null','-'],capture_output=True,text=True,check=True)
 return json.loads(re.findall(r'\{\s*"input_i".*?\}',r.stderr,re.S)[-1])
def dec(p,af=None):
 c=['ffmpeg','-v','error','-i',str(p)]
 if af:c+=['-af',af]
 return np.frombuffer(subprocess.check_output(c+['-f','f32le','-acodec','pcm_f32le','-']),dtype='<f4').reshape(-1,2)
rows=json.loads((Q/'downloads.json').read_text());reports=[]
for r in rows:
 src=V/r['output'];out=src.with_suffix('.wav');report=Q/(r['locale']+'-'+r['id']+'-measurement.json')
 if report.exists():
  old=json.loads(report.read_text());assert sha(src)==old['source_sha256'] and sha(out)==old['wav_sha256'];reports.append(old);continue
 assert not out.exists()
 assert sha(src)==sha(Path(r['download']))
 before=measure(src,base);gain=min(-16-float(before['input_i']),-1.2-float(before['input_tp']))
 limited=float(before['input_i'])+gain < -16.5
 if limited:
  filt=base+f",loudnorm=I=-16:TP=-1.2:LRA=11:measured_I={before['input_i']}:measured_TP={before['input_tp']}:measured_LRA={before['input_lra']}:measured_thresh={before['input_thresh']}:offset={before['target_offset']}:linear=false"
 else:filt=base+f',volume={gain:.8f}dB'
 subprocess.run(['ffmpeg','-n','-v','error','-i',str(src),'-af',filt,'-ar',str(R),'-ac','2','-c:a','pcm_s24le',str(out)],check=True)
 native=dec(src,base);actual=dec(out);after=measure(out)
 assert actual.shape==native.shape,(r['id'],'duration changed')
 assert abs(float(after['input_i'])+16)<=.5 and float(after['input_tp'])<=-1.15,(r['id'],after)
 error=None if limited else float(np.max(np.abs(actual.astype('float64')-native.astype('float64')*10**(gain/20))))
 if error is not None:assert error<2e-6
 # Signal support is diagnostic only: never use this threshold to crop a source.
 peak=np.max(np.abs(actual),axis=1);active=np.flatnonzero(peak>10**(-45/20))
 d={**r,'model':'speech-2.8-hd','voice_name':'BOI-HK-v13-R06-Clone-r01','voice_id':'moss_audio_26a453eb-d110-11f1-bf7a-5699d2bd1137','pitch':0,'volume':1,'source_sha256':sha(src),'wav':str(out.relative_to(V)),'wav_sha256':sha(out),'sample_rate':R,'channels':2,'frames':len(actual),'duration':len(actual)/R,'source_loudness':before,'loudness':after,'processing':{'kind':'dynamic_loudnorm_peak_control' if limited else 'constant_gain','gain_db':None if limited else gain,'no_time_stretch':True,'no_pitch_shift':True,'no_trim':True,'full_resampled_source_frames_preserved':True,'constant_gain_max_error':error},'diagnostic_activity_minus45dB':{'start':int(active[0])/R if len(active) else None,'end':(int(active[-1])+1)/R if len(active) else None},'approval':'Generated under approved cloned voice; individual clip not yet user-reviewed.'}
 report.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');reports.append(d)
summary={'normalized_clips':len(reports),'total_frames':sum(x['frames'] for x in reports),'records':reports}
(Q/'measurements.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'normalized':len(reports),'latest':[{'locale':r['locale'],'id':r['id'],'seconds':round(r['duration'],3),'LUFS':r['loudness']['input_i'],'TP':r['loudness']['input_tp']} for r in reports[-4:]]},ensure_ascii=False))
