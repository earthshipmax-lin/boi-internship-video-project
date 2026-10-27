"""Inspect the raw r05 narration and shorten only long low-level internal silence.
Never changes speaking rate, pitch, or the beginning/final tail. Keeps raw MP3.
"""
from pathlib import Path
import array, hashlib, json, re, subprocess, sys, wave

base = Path(__file__).resolve().parents[1]
qa = base / 'qa/v11/voice-r05'
raw = qa / 'full-source.mp3'
output = qa / 'full-short-pauses.wav'
if not raw.exists():
    raise SystemExit('Download full-source.mp3 before running.')
if output.exists():
    raise SystemExit('Refusing to overwrite an existing output.')
probe = json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=sample_rate,channels,codec_name','-of','json',str(raw)]))
rate = int(probe['streams'][0]['sample_rate'])
# Detect only low-level quiet; retain quiet syllable endings and inhalations.
result = subprocess.run(['ffmpeg','-hide_banner','-i',str(raw),'-af','silencedetect=noise=-48dB:d=0.12','-f','null','-'], capture_output=True, text=True, check=True)
(qa/'silence-raw.log').write_text(result.stderr)
starts = [float(v) for v in re.findall(r'silence_start: ([\d.]+)',result.stderr)]
ends = [float(v) for v in re.findall(r'silence_end: ([\d.]+)',result.stderr)]
intervals = list(zip(starts, ends))
duration = float(probe['format']['duration'])
# Keep 0.4s quiet on each side of a cut. No speech/tail trimmed.
cuts = [(a+0.4, b-0.4) for a,b in intervals if b-a>1.0 and a>0.05 and b<duration-0.05]
pcm = subprocess.check_output(['ffmpeg','-v','error','-i',str(raw),'-ac','1','-ar',str(rate),'-f','s16le','-'])
spans=[]; cursor=0
for a,b in cuts:
    start=round(a*rate)*2; end=round(b*rate)*2
    spans.append(pcm[cursor:start]); cursor=end
spans.append(pcm[cursor:]); processed=b''.join(spans)
with wave.open(str(output),'wb') as w:
    w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes(processed)
after = subprocess.run(['ffmpeg','-hide_banner','-i',str(output),'-af','silencedetect=noise=-48dB:d=0.12','-f','null','-'],capture_output=True,text=True,check=True)
(qa/'silence-output.log').write_text(after.stderr)
post_starts=[float(v) for v in re.findall(r'silence_start: ([\d.]+)',after.stderr)]
post_ends=[float(v) for v in re.findall(r'silence_end: ([\d.]+)',after.stderr)]
post_intervals=list(zip(post_starts,post_ends))
internal=[b-a for a,b in post_intervals if a>0.05 and b<len(processed)/(2*rate)-0.05]
report={'raw_file':str(raw.relative_to(base)), 'raw_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(), 'probe':probe, 'silence_threshold_db':-48,'silence_detection_min_s':0.12,'raw_silence_intervals_s':intervals,'removed_internal_silence_spans_s':cuts,'output_file':str(output.relative_to(base)), 'output_duration_s':len(processed)/(2*rate),'removed_s':(len(pcm)-len(processed))/(2*rate),'sample_rate':rate,'channels':1,'output_internal_quiet_max_s_at_threshold':max(internal,default=0),'speech_processing':'None: exact retained PCM spans; 1x, no pitch, compression, reverb or speech fades. Beginning and final tail retained.','decode_ok':True,'limits':'Threshold-based quiet detection does not prove perceived pause duration, Cantonese correctness, vocal naturalness, or emotional effect.'}
(qa/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['output_duration_s','removed_s','removed_internal_silence_spans_s','output_internal_quiet_max_s_at_threshold']},ensure_ascii=False))
