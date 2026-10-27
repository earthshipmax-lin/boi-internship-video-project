from pathlib import Path
import subprocess,json,re
import numpy as np

R=Path(__file__).resolve().parents[1];Q=R/'qa/v12/stage3';D=R/'public/music/v12-stage3';D.mkdir(exist_ok=True)
def run(args):
    p=subprocess.run(args,capture_output=True,text=True)
    if p.returncode:raise RuntimeError(p.stderr)
    return p
def read(p):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-ar','48000','-ac','2','-f','f32le','-']),dtype='<f4').reshape(-1,2)
def write(p,a):
    assert not p.exists(),p
    subprocess.run(['ffmpeg','-v','error','-f','f32le','-ar','48000','-ac','2','-i','-','-c:a','pcm_s24le',str(p)],input=a.astype('<f4').tobytes(),check=True,capture_output=True)

voice=read(R/'qa/v12/voice-timeline.wav');rate=48000;extra=100800
# The next sentence already starts before the nominal map cut. Insert in the
# actual quiet gap, never at the scene cut, which would split spoken audio.
lo,hi=round(28.18*rate),round(28.28*rate)
cut=lo+int(np.argmin(np.max(np.abs(voice[lo:hi]),axis=1)))
new_voice=np.concatenate([voice[:cut],np.zeros((extra,2),dtype=np.float32),voice[cut:]])
vp=Q/'voice-timeline.wav'
if not vp.exists():write(vp,new_voice)
decoded=read(vp)
assert np.array_equal(decoded[:cut],voice[:cut]) and np.array_equal(decoded[cut+extra:],voice[cut:])
assert len(decoded)==round(70.1*rate)

# Extend the first selected passage of A naturally into the original recording;
# keep all later passages and the existing 0.4s musical crossfades.
meta=json.loads((R/'src/config/beats-v11.json').read_text());spans=[(x['source_start'],x['source_end']) for x in meta['spans']];spans[0]=(spans[0][0],spans[0][1]+2.1)
parts=[f'[0:a]atrim=start={a}:end={b},asetpts=PTS-STARTPTS[a{i}]' for i,(a,b) in enumerate(spans)]
parts+=['[a0][a1]acrossfade=d=0.4:c1=qsin:c2=qsin[x1]','[x1][a2]acrossfade=d=0.4:c1=qsin:c2=qsin[x2]','[x2][a3]acrossfade=d=0.4:c1=qsin:c2=qsin,apad,atrim=duration=70.1,afade=t=in:d=1,afade=t=out:st=68.7:d=1.4[out]']
music=D/'A-edit-70.1s.wav';assert not music.exists()
run(['ffmpeg','-v','error','-i',str(R/'public/music/v11/bgm-A.mp3'),'-filter_complex',';'.join(parts),'-map','[out]','-ar','48000','-ac','2','-c:a','pcm_s24le',str(music)])
mix=Q/'mix-pre-normalize.wav';assert not mix.exists();gain=.70*10**(-1.5/20)
graph=f'[1:a]asplit=2[vo][sc];[0:a]volume={gain}[bg];[bg][sc]sidechaincompress=threshold=.028:ratio=3:attack=25:release=450:knee=2:makeup=1[duck];[duck][vo]amix=inputs=2:normalize=0:duration=longest[out]'
run(['ffmpeg','-v','error','-i',str(music),'-i',str(vp),'-filter_complex',graph,'-map','[out]','-ar','48000','-c:a','pcm_s24le',str(mix)])
first=run(['ffmpeg','-hide_banner','-i',str(mix),'-af','loudnorm=I=-14.5:TP=-1.3:LRA=11:print_format=json','-f','null','-']).stderr
m=json.loads(re.findall(r'\{[\s\S]*?\}',first)[-1]);(Q/'loudness-first.json').write_text(json.dumps(m,indent=2)+'\n')
af=f"loudnorm=I=-14.5:TP=-1.3:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true:print_format=json"
out=D/'review-mix.wav';assert not out.exists();result=run(['ffmpeg','-hide_banner','-i',str(mix),'-af',af,'-ar','48000','-c:a','pcm_s24le',str(out)]);(Q/'loudness-final.log').write_text(result.stderr)
record={'duration':70.1,'insert_seconds':2.1,'voice_insert_source_sample':cut,'voice_insert_source_seconds':cut/rate,'insert_boundary_peak_dbfs':float(20*np.log10(max(np.abs(voice[cut]).max(),1e-12))),'voice_retained_samples_identical_before_and_after_insert':True,'voice_rate':1,'voice_pitch_change':False,'voice_tail_cut':False,'voice_source':'qa/v12/voice-timeline.wav','music_source':'selected A only','music_spans':spans,'music_extension':'First original A passage extended by 2.1 seconds; later passages unchanged, 0.4s crossfades retained. No looped voice or frozen mix.','sidechain':'same settings as accepted Stage1','bgm_bus_gain':gain,'caption_shift_rule':'unchanged through trust speech; all phrases starting after 28.2s shifted +2.1s','semantic_alignment':'Original narration samples kept in order, 1x, with matching downstream captions and map clock; no semantic rearrangement introduced.'}
(Q/'audio-edit.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print(json.dumps(record,ensure_ascii=False,indent=2))
