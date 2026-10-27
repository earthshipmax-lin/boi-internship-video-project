from pathlib import Path
import json,subprocess,hashlib,math
import numpy as np
V=Path(__file__).resolve().parents[1];Q=V/'qa/v19/film';Q.mkdir(parents=True,exist_ok=True);D=V/'public/music/hk-v19';D.mkdir(exist_ok=True);SR=48000;at=4312000

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-f','f32le','-ar','48000','-ac','2','-']),dtype='<f4').reshape(-1,2).copy()
def write(p,a):
 if p.exists():
  assert np.array_equal(read(p),np.round(a*8388608).clip(-8388608,8388607)/8388608) or np.max(np.abs(read(p)-a))<2e-7,p
  return
 subprocess.run(['ffmpeg','-v','error','-n','-f','f32le','-ar','48000','-ac','2','-i','-','-c:a','pcm_s24le',str(p)],input=a.astype('<f4').tobytes(),check=True)
def loud(p):
 r=subprocess.run(['ffmpeg','-hide_banner','-i',str(p),'-af','loudnorm=I=-16:TP=-1:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
 return json.JSONDecoder().raw_decode(r.stderr[r.stderr.rfind('{'):])[0]
baseline=json.loads((V/'qa/v19/round2/protected-baseline.json').read_text())
for p in list((V/'public/music/hk-v16').glob('*.wav'))+[V/'src/config/timeline-v16-cn.json',V/'src/scenes/EpicFilmEndingV16.tsx',V/'src/index-v16.tsx',V/'out/BOI-HK_史詩形象片_v16_普通話_遞進拖音版.mp4',V/'qa/v19/ending-candidate-1.wav',V/'qa/v19/ending-candidate-2.wav']:baseline[str(p.relative_to(V))]=sha(p)
(Q/'protected-baseline.json').write_text(json.dumps(baseline,indent=2)+'\n')
c=json.loads((V/'qa/v19/round2/composition-report.json').read_text())['candidates'][0];assert sha(V/c['file'])==c['sha256'];selected=read(V/c['file']);old=read(V/'public/music/hk-v16/cn-master.wav');voice=np.zeros_like(old[at:]);voice[:len(selected)]=selected;write(D/'ending-voice.wav',voice)
# Existing A score, original fade and restrained music level. Feed scaled VO to detector
# so its duck response remains comparable to the previous pre-master voice.
music=read(V/'public/music/hk-v16/ending-music.wav');write(D/'ending-music.wav',music)
graph='[1:a]asplit=2[vo][det];[det]volume=0.4634566[sc];[0:a]volume=1.2708849[bg];[bg][sc]sidechaincompress=threshold=.028:ratio=3:attack=25:release=450:knee=2:makeup=1[duck];[duck][vo]amix=inputs=2:normalize=0:duration=longest[out]'
if not (D/'ending-pre-master.wav').exists():subprocess.run(['ffmpeg','-v','error','-n','-i',str(D/'ending-music.wav'),'-i',str(D/'ending-voice.wav'),'-filter_complex',graph,'-map','[out]','-ar','48000','-c:a','pcm_s24le',str(D/'ending-pre-master.wav')],check=True)
lm=loud(D/'ending-pre-master.wav');gain=-16-float(lm['input_i']);write(D/'ending-scaled.wav',read(D/'ending-pre-master.wav')*10**(gain/20))
subprocess.run(['ffmpeg','-v','error','-n','-i',str(D/'ending-scaled.wav'),'-af','alimiter=limit=.85:attack=5:release=60:level=false:latency=true','-ar','48000','-c:a','pcm_s24le',str(D/'ending-limited.wav')],check=True)
ending=read(D/'ending-limited.wav');master=old.copy();master[at:]=ending;w=np.linspace(0,1,1920)[:,None];master[at:at+1920]=old[at:at+1920]*(1-w)+ending[:1920]*w;write(D/'cn-master.wav',master)
oldvoice=read(V/'public/music/hk-v16/cn-voice.wav');oldvoice[at:]=voice;write(D/'cn-voice.wav',oldvoice)
t=json.loads((V/'src/config/timeline-v16-cn.json').read_text());p=c['placements'];start=at/SR
for cue,a,b in [(t['cues'][-2],p[0],p[1]),(t['cues'][-1],p[2],p[2])]:
 cue.update(startFrame=math.floor((start+a['speechStartSeconds']-.04)*30),endFrame=math.ceil((start+b['speechEndSeconds']+.15)*30),speechStart=start+a['speechStartSeconds'],speechEnd=start+b['speechEndSeconds'])
t['status']='v19_user_selected_candidate1_ending';(V/'src/config/timeline-v19-cn.json').write_text(json.dumps(t,ensure_ascii=False,indent=2)+'\n')
for a,b in [('src/scenes/EpicFilmEndingV16.tsx','src/scenes/EpicFilmEndingV19.tsx'),('src/index-v16.tsx','src/index-v19.tsx')]:
 s=(V/a).read_text().replace('V16','V19').replace('v16','v19');(V/b).write_text(s)
s=(V/'scripts/render-ending-v16.mjs').read_text().replace('qa/v16','qa/v19/film').replace('v16','v19').replace('遞進拖音預覽','雄渾重錄15秒預覽').replace("[timeline.cues.find(c=>c.id==='caption-22').startFrame-8,timeline.durationInFrames-1]","[2512,timeline.durationInFrames-1]")
(V/'scripts/render-ending-v19.mjs').write_text(s)
(Q/'audio-implementation.json').write_text(json.dumps({'selected':c,'insertStartSeconds':start,'bodySamplesUnchanged':at,'staticEndingMixGainDB':gain,'endingMixLoudness':loud(D/'ending-limited.wav'),'noRetiming':True,'noPitchShift':True,'noCrescendo':True,'finalTwoCues':t['cues'][-2:],'music':'Existing A score and original fade; same nominal master music scale and duck curve.'},ensure_ascii=False,indent=2)+'\n')
(V/'qa/v19/COMPLETE_ENDING_SELECTION.json').write_text(json.dumps({'date':'2026-10-27','userReply':'候选1：三句A参数，品牌名低音高','selected':c['file'],'sha256':c['sha256'],'authorization':'Integrate selected full ending into V19; not final film approval','disclosedLimit':'Natural 山 tail about0.37s remains below script0.6–0.8s; selection made after disclosure.'},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'gain':gain,'endingMix':loud(D/'ending-limited.wav'),'cues':t['cues'][-2:]},ensure_ascii=False))
