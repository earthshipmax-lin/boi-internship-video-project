from pathlib import Path
import hashlib,json,subprocess,re
import torch,whisper
V=Path(__file__).resolve().parents[1];Q=V/'qa/v19';report={'phase':'round1_only','model':'speech-2.8-hd','voice':'BOI-HK-v13-R06-Clone-r01','script':'大展——宏圖。','creditUse':33,'creditsBefore':6549,'creditsAfter':6516,'takes':{},'policy':'Only line1 A/B/C generated. No WSOLA/time-stretch/positive pitch/crescendo. Auditions receive loudness normalization only; original sources retained. No EQ or hall reverb at line1 direction-selection stage.'}
params={'A':(.82,-1,None,6549,6538),'B':(.85,0,None,6538,6527),'C':(.80,-1,'neutral',6527,6516)}
def measure(p):
 r=subprocess.run(['ffmpeg','-hide_banner','-i',str(p),'-af','aformat=channel_layouts=stereo,loudnorm=I=-16:TP=-1.3:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True);return json.loads(re.findall(r'\{\s*"input_i".*?\}',r.stderr,re.S)[-1])
def duration(p):return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(p)]))
torch.set_num_threads(4);model=whisper.load_model('small',device='cpu',download_root=str(V/'.model-cache'))
for name,(speed,pitch,emotion,before,after) in params.items():
 src=Q/f'sources/line1-{name}-source.wav';out=Q/f'auditions/line1-{name}.wav';assert not out.exists();m=measure(src)
 gain=-16-float(m['input_i']);assert float(m['input_tp'])+gain<=-1,(name,'Needs peak treatment before equal loudness')
 af=f'aformat=channel_layouts=stereo,volume={gain}dB'
 subprocess.run(['ffmpeg','-v','error','-n','-i',str(src),'-af',af,'-ar','48000','-ac','2','-c:a','pcm_s24le',str(out)],check=True)
 post=measure(out);assert abs(float(post['input_i'])+16)<=.5 and float(post['input_tp'])<=-1;assert abs(duration(src)-duration(out))<.00006
 transcript=model.transcribe(str(out),language='zh',fp16=False,verbose=None)['text'];norm=re.sub(r'[^\u4e00-\u9fff]','',transcript).replace('圖','图').replace('紅','红');text_ok=norm in ['大展宏图','大展红图','大展洪图']
 info={'source':str(src.relative_to(V)),'file':str(out.relative_to(V)),'sourceSHA256':hashlib.sha256(src.read_bytes()).hexdigest(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'seconds':duration(out),'sourceSeconds':duration(src),'speed':speed,'pitch':pitch,'emotion':emotion,'volume':1,'creditsBefore':before,'creditsAfter':after,'credits':before-after,'ASR':transcript,'ASRAcceptedExactOrAllowedHomophone':text_ok,'integratedLUFS':float(post['input_i']),'truePeakDBTP':float(post['input_tp']),'processing':['R128 measurement after stereo conversion, static gain to -16LUFS; no dynamics or retiming','48k stereo24bit PCM export'],'sourceRetime':False,'proof':f'qa/v19/proofs/line1-{name}.png'}
 report['takes'][name]=info;print(name,transcript,post['input_i'],post['input_tp'],flush=True)
report['CDeviation']='UI offered Neutral, not Calm. Section3 permits neutral; C uses Neutral and is explicitly labelled. No claim of applying calm.'
(Q/'audition-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');assert all(x['ASRAcceptedExactOrAllowedHomophone'] for x in report['takes'].values()),'At least one ASR take requires review; do not claim all passed.'
