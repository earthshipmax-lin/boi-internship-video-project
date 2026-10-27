from pathlib import Path
import json,shutil,subprocess,re,hashlib
import torch,whisper
V=Path(__file__).resolve().parents[1];Q=V/'qa/v19';R=Q/'rejected/line1-A-take01';R.mkdir(parents=True,exist_ok=True)
for rel in ['sources/line1-A-source.wav','auditions/line1-A.wav','proofs/line1-A.png']:
 p=Q/rel;shutil.move(str(p),str(R/p.name))
report=json.loads((Q/'audition-verification.json').read_text());(R/'original-audit.json').write_text(json.dumps(report['takes']['A'],ensure_ascii=False,indent=2)+'\n')
src=Q/'sources/line1-A-source.wav';shutil.copy2('/Users/linwenbin/Downloads/MiniMax_2026-10-27_09_31_48_BOI-HK-v13-R06-Clone-r01.wav',src)
def measure(p):
 x=subprocess.run(['ffmpeg','-hide_banner','-i',str(p),'-af','aformat=channel_layouts=stereo,loudnorm=I=-16:TP=-1.3:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True);return json.loads(re.findall(r'\{\s*"input_i".*?\}',x.stderr,re.S)[-1])
m=measure(src);gain=-16-float(m['input_i']);assert float(m['input_tp'])+gain<=-1
out=Q/'auditions/line1-A.wav';subprocess.run(['ffmpeg','-v','error','-n','-i',str(src),'-af',f'aformat=channel_layouts=stereo,volume={gain}dB','-ar','48000','-ac','2','-c:a','pcm_s24le',str(out)],check=True);post=measure(out);assert abs(float(post['input_i'])+16)<=.5 and float(post['input_tp'])<=-1
torch.set_num_threads(4);model=whisper.load_model('small',device='cpu',download_root=str(V/'.model-cache'));transcript=model.transcribe(str(out),language='zh',fp16=False,verbose=None)['text'];norm=re.sub(r'[^\u4e00-\u9fff]','',transcript).replace('圖','图').replace('紅','红');ok=norm in ['大展宏图','大展红图','大展洪图'];a=report['takes']['A'];a.update(sourceSHA256=hashlib.sha256(src.read_bytes()).hexdigest(),sha256=hashlib.sha256(out.read_bytes()).hexdigest(),creditsBefore=6516,creditsAfter=6505,ASR=transcript,ASRAcceptedExactOrAllowedHomophone=ok,integratedLUFS=float(post['input_i']),truePeakDBTP=float(post['input_tp']),selectedTake=2,script='大展——宏圖，',reason='First take ASR read 圖 as 土; same A parameters with comma from target reading regenerated naturally.')
a['seconds']=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(out)]));a['sourceSeconds']=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(src)]));a['proof']='qa/v19/proofs/line1-A-take02.png'
report.update(creditUse=44,creditsAfter=6505,rejectedCredits=11,productionCredits=33,rejectedTakes=[{'variant':'A','take':1,'reason':'ASR 圖/土 ambiguity','path':'qa/v19/rejected/line1-A-take01','credits':11}]);(Q/'audition-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('A TAKE2',transcript,post['input_i'],post['input_tp'],flush=True);assert ok,'A take2 still requires phonetic review'
