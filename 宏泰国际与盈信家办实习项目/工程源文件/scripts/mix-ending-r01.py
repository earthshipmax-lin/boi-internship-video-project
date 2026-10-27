from pathlib import Path
import subprocess,json,re,shutil
R=Path(__file__).resolve().parents[1];q=R/'qa/closing-r01';dest=R/'public/music/closing-r01'
def run(cmd):return subprocess.run(cmd,check=True,capture_output=True,text=True)
def wav(inputs,graph,out):
 if out.exists():raise RuntimeError(f'Refusing overwrite: {out}')
 cmd=['ffmpeg','-v','error']
 for f in inputs:cmd+=['-i',str(f)]
 run(cmd+['-filter_complex',graph,'-map','[out]','-ar','48000','-ac','2','-c:a','pcm_s24le',str(out)])
voice=q/'voice-timeline.wav'
# 55.90s is a quiet boundary after the preceding sentence; old slogan is replaced.
# No speech is time-stretched or pitch shifted. Keep the whole new MP3 including its tail.
wav([R/'qa/v11/voice-r06/full-source.mp3',q/'ending-source.mp3'],
 '[0:a]atrim=end=55.9,aresample=48000,adelay=2400|2400,apad,atrim=duration=68[old];'
 '[1:a]aresample=48000,volume=0.5dB,adelay=58500|58500,apad,atrim=duration=68[new];'
 '[old][new]amix=inputs=2:normalize=0[out]',voice)
shutil.copy2(q/'ending-source.mp3',R/'public/vo/closing-r01/ending-source.mp3')
mix=q/'mix-pre-normalize.wav'
# v11 used 0.70; -1.5 dB is a small, measurable reduction confined to the BGM bus.
bg_gain=.70*10**(-1.5/20)
wav([R/'public/music/v11/A-edit-68s.wav',voice],
 f'[1:a]asplit=2[vo][sc];[0:a]volume={bg_gain}[bg];'
 '[bg][sc]sidechaincompress=threshold=0.028:ratio=3:attack=25:release=450:knee=2:makeup=1[duck];'
 '[duck][vo]amix=inputs=2:normalize=0:duration=longest[out]',mix)
first=run(['ffmpeg','-hide_banner','-i',str(mix),'-af','loudnorm=I=-14.5:TP=-1.3:LRA=11:print_format=json','-f','null','-']).stderr
m=json.loads(re.findall(r'\{[\s\S]*?\}',first)[-1]);(q/'mix-loudness-first.json').write_text(json.dumps(m,indent=2)+'\n')
af=f"loudnorm=I=-14.5:TP=-1.3:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true:print_format=json"
output=dest/'review-mix.wav'
if output.exists():raise RuntimeError('Refusing overwrite of mix')
r=run(['ffmpeg','-hide_banner','-i',str(mix),'-af',af,'-ar','48000','-c:a','pcm_s24le',str(output)])
(q/'mix-loudness-final.log').write_text(r.stderr)
caps=json.loads((R/'src/config/captions-v11.json').read_text())[:22]
caps += [{'text':'大展宏圖，穩如泰山','start':58.50,'end':61.42},{'text':'宏泰國際','start':61.90,'end':63.50}]
(R/'src/config/captions-ending-r01.json').write_text(json.dumps(caps,ensure_ascii=False,indent=2)+'\n')
(q/'audio-edit.json').write_text(json.dumps({'duration':68,'old_voice_source_end':55.9,'old_voice_timeline_end':58.3,'new_voice_timeline_start':58.5,'new_voice_gain_db':.5,'new_voice_generation_speed':.9,'post_generation_time_stretch':False,'music_source':'A only, same 68s edit','music_bus_change_db':-1.5,'music_bus_gain':bg_gain,'sidechain':'same as v11','caption_method':'Reference-text alignment; not independent Cantonese verification','integrated_target_lufs':-14.5,'true_peak_target_dbtp':-1.3},ensure_ascii=False,indent=2)+'\n')
print('68s mix and closing captions ready')
