from pathlib import Path
import json,subprocess,re,hashlib
ROOT=Path(__file__).resolve().parents[1];q=ROOT/'qa/v11/film';music=ROOT/'public/music/v11/bgm-A.mp3';voice=ROOT/'public/vo/hk-v11/full-r06.mp3'
meta=json.loads((q/'music-A-analysis.json').read_text());onsets=meta['onsets_s']
near=lambda t:min(onsets,key=lambda x:abs(x-t))
# Preserve an opening, developed orchestral passage, late climax and resolved tail.
spans=[(0,near(29)),(near(70),near(91)),(near(128),near(142)),(near(149.18),meta['duration_s'])]
fades=.4;timeline=[];cursor=0
for i,(start,end) in enumerate(spans):
 timeline.append({'source_start':start,'source_end':end,'timeline_start':round(cursor,5),'timeline_end':round(cursor+end-start,5)})
 cursor+=end-start-fades if i<len(spans)-1 else end-start
filters=[]
for i,(a,b) in enumerate(spans):filters.append(f'[0:a]atrim=start={a}:end={b},asetpts=PTS-STARTPTS[a{i}]')
filters+=['[a0][a1]acrossfade=d=0.4:c1=qsin:c2=qsin[x1]','[x1][a2]acrossfade=d=0.4:c1=qsin:c2=qsin[x2]','[x2][a3]acrossfade=d=0.4:c1=qsin:c2=qsin,apad,atrim=duration=68,afade=t=in:d=1.0,afade=t=out:st=66.6:d=1.4[music]']
edit=ROOT/'public/music/v11/A-edit-68s.wav'
if edit.exists():raise SystemExit('Refusing overwrite of existing music edit')
subprocess.run(['ffmpeg','-v','error','-i',str(music),'-filter_complex',';'.join(filters),'-map','[music]','-ar','48000','-ac','2',str(edit)],check=True)
# Voice remains 1x and complete, start offset 2.4s; duck the orchestra using that unprocessed voice.
mix=q/'mix-pre-normalize.wav';graph='[1:a]aresample=48000,adelay=2400|2400,apad,atrim=duration=68,asplit=2[vo][sc];[0:a]volume=0.70[bg];[bg][sc]sidechaincompress=threshold=0.028:ratio=3:attack=25:release=450:knee=2:makeup=1[duck];[duck][vo]amix=inputs=2:normalize=0:duration=longest[out]'
subprocess.run(['ffmpeg','-v','error','-i',str(edit),'-i',str(voice),'-filter_complex',graph,'-map','[out]','-ar','48000','-ac','2',str(mix)],check=True)
first=subprocess.run(['ffmpeg','-hide_banner','-i',str(mix),'-af','loudnorm=I=-14:TP=-1:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True).stderr
metrics=json.loads(re.findall(r'\{[\s\S]*?\}',first)[-1]);(q/'mix-loudness-first.json').write_text(json.dumps(metrics,indent=2)+'\n')
filter2=f"loudnorm=I=-14:TP=-1:LRA=11:measured_I={metrics['input_i']}:measured_TP={metrics['input_tp']}:measured_LRA={metrics['input_lra']}:measured_thresh={metrics['input_thresh']}:offset={metrics['target_offset']}:linear=true:print_format=json"
output=ROOT/'public/music/v11/review-mix.wav'
r=subprocess.run(['ffmpeg','-hide_banner','-i',str(mix),'-af',filter2,'-ar','48000','-c:a','pcm_s24le',str(output)],capture_output=True,text=True,check=True)
(q/'mix-loudness-final.log').write_text(r.stderr)
headroom=ROOT/'public/music/v11/review-mix-headroom.wav'
subprocess.run(['ffmpeg','-v','error','-i',str(output),'-af','volume=-0.25dB','-c:a','pcm_s24le',str(headroom)],check=True)
map_onsets=[]
for j,span in enumerate(timeline):
 for source_time in onsets:
  if span['source_start']<=source_time<span['source_end']:
   t=span['timeline_start']+source_time-span['source_start']
   if 0<=t<68:map_onsets.append(round(t,5))
record={'source':'A only; B/C not loaded','spans':timeline,'crossfade_s':fades,'edited_source_duration_s':cursor,'output_duration_s':68,'onsets_s':sorted(map_onsets),'voice_offset_s':2.4,'voice_playback_rate':1,'voice_file':'vo/hk-v11/full-r06.mp3','music_edit':'music/v11/A-edit-68s.wav','mix':'music/v11/review-mix-headroom.wav','global_headroom_gain_db':-.25,'notes':'Spectral onsets are candidate transient points, not certified musical downbeats. Music transitions need subjective review. Voice uncut, only music sidechain ducking and global loudness normalization.'}
(ROOT/'src/config/beats-v11.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('Music spans:',timeline,'source duration',cursor,flush=True)
print('Final mix ready',output,flush=True)
