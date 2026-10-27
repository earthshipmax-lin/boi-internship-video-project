from pathlib import Path
import subprocess,json
V=Path(__file__).resolve().parents[1];Q=V/'qa/v19/film';a=Q/'picture-prefix-v16.mp4';b=Q/'ending-picture-suffix.mp4';out=V/'out/BOI-HK_史詩形象片_v19_普通話_片尾重錄版.mp4';assert not out.exists()
for p,n in [(a,2510),(b,452)]:
 s=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(p)]))['streams'];v=next(x for x in s if x['codec_type']=='video');assert int(v['nb_frames'])==n
# The source frame2510 at83.666667s is a closed-GOP I-frame boundary.
concat=Q/'picture-concat.txt';concat.write_text("file 'picture-prefix-v16.mp4'\nfile 'ending-picture-suffix.mp4'\n")
subprocess.run(['ffmpeg','-v','error','-n','-f','concat','-safe','0','-i',str(concat),'-i',str(V/'public/music/hk-v19/cn-master.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','320k','-ar','48000','-movflags','+faststart',str(out)],check=True)
s=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(out)]));v=next(x for x in s['streams'] if x['codec_type']=='video');assert int(v['nb_frames'])==2962 and abs(float(v['duration'])-98.733333)<1e-5
# Compare full decoded prefix to original V16, not only sampled pictures.
def frame_hashes(p):return subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:v:0','-frames:v','2510','-f','framemd5','-']).decode().splitlines()
old=frame_hashes(V/'out/BOI-HK_史詩形象片_v16_普通話_遞進拖音版.mp4');new=frame_hashes(out);old=[r.split(',')[-1].strip() for r in old if not r.startswith('#')];new=[r.split(',')[-1].strip() for r in new if not r.startswith('#')];assert len(old)==len(new)==2510 and old==new
(Q/'picture-prefix-parity.json').write_text(json.dumps({'prefixFrames':2510,'prefixSeconds':2510/30,'allDecodedPrefixFrameHashesEqualToV16':True,'suffixFrames':452,'finalFrames':2962,'method':'Original V16 H264 prefix copied at existing I-frame boundary. Only suffix pictures re-rendered for final subtitles, then video streams concatenated without full-frame re-encode.'},indent=2)+'\n');print('V19 complete; prefix frame hashes identical to V16.')
