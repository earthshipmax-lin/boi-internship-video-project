"""Verify encoded narration against source at normal speed using FFT correlation.
Requires NumPy; no online access. Run after the v4 render exits successfully.
"""
from pathlib import Path
import json,subprocess,wave,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
movie=ROOT/'out/BOI-HK_MiniMax粵語_中英Logo_v4.mp4'
qa=ROOT/'qa/v4'
def run(*a):return subprocess.run(list(map(str,a)),capture_output=True,check=True)
def read(p):
 with wave.open(str(p),'rb') as w:
  assert w.getnchannels()==1 and w.getsampwidth()==2 and w.getframerate()==48000
  return np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float)/32768
probe=json.loads(run('ffprobe','-v','error','-show_streams','-show_format','-of','json',movie).stdout)
v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio')
assert v['codec_name']=='h264' and int(v['width'])==1920 and int(v['height'])==1080 and int(v['nb_frames'])==2253 and v['r_frame_rate']=='30/1'
assert a['codec_name']=='aac' and int(a['sample_rate'])==48000
run('ffmpeg','-v','error','-i',movie,'-f','null','-')
target=qa/'voiced-output.wav';run('ffmpeg','-v','error','-y','-i',movie,'-vn','-ar','48000','-ac','1','-c:a','pcm_s16le',target)
content=json.loads((qa/'content-audit.json').read_text())
y=read(target);provenance=json.loads((ROOT/'public/vo/hk-v4/VOICE_PROVENANCE.json').read_text());timeline=json.loads((qa/'timeline.json').read_text());results=[]
for s in timeline['scenes']:
 filename=f"vo/hk-v4/VO-{int(s['id'][1:]):02d}.wav";source=ROOT/'public'/filename;x=read(source);rec=provenance['segments'][filename]
 assert hashlib.sha256(source.read_bytes()).hexdigest()==rec['sha256']
 # Read the exact JS frame quantization from the active config audit, rather than
 # re-rounding the higher-precision presentation timeline with Python.
 expected=next(c for c in content['scenes'] if c['id']==s['id'])['voiceStartFrame']/30;pad=.18;left=round((expected-pad)*48000);window=y[left:left+len(x)+round(pad*96000)]
 n=1<<(len(window)+len(x)-2).bit_length();corr=np.fft.irfft(np.fft.rfft(window,n)*np.fft.rfft(x[::-1],n),n)[len(x)-1:len(window)]
 lag=int(np.argmax(corr));actual=(left+lag)/48000;matched=window[lag:lag+len(x)];coef=float(np.dot(x,matched)/np.sqrt(np.dot(x,x)*np.dot(matched,matched)))
 assert abs(actual-expected)<.02 and coef>.97,(s['id'],actual-expected,coef)
 results.append({'scene':s['id'],'expectedStart':expected,'detectedStart':actual,'offsetMs':round((actual-expected)*1000,3),'sourceCorrelationAt1x':coef,'voiceDuration':len(x)/48000})
peak=float(np.max(np.abs(y)));assert peak<1
report={'movie':str(movie),'durationVideo':float(v['duration']),'durationContainer':float(probe['format']['duration']),'frames':int(v['nb_frames']),'videoCodec':v['codec_name'],'audioCodec':a['codec_name'],'sampleRate':48000,'decode':'PASS','peakDbFS':float(20*np.log10(peak)),'speechRate':'1x source audio correlation confirmed for all 7 segments','segments':results,'sha256':hashlib.sha256(movie.read_bytes()).hexdigest()}
(qa/'voice-sync.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
