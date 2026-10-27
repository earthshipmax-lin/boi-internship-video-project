from pathlib import Path
import subprocess,json
V=Path(__file__).resolve().parents[1];t=json.loads((V/'src/config/timeline-v14-yue.json').read_text());movie=V/'out/BOI-HK_史詩形象片_v14_粵語_節奏與同步精修版.mp4';out=V/'out/BOI-HK_v14_平台與樹形生長_重點預覽.mp4'
cues={r['id']:r for r in t['cues']};a=min(t['sceneStarts']['platform'],cues['caption-14']['startFrame'])/30-.15;b=t['sceneStarts']['paper']/30;c=min(t['sceneStarts']['roots'],cues['caption-21']['startFrame'])/30-.15;d=t['durationSeconds']
graph=f'[0:v]trim=start={a}:end={b},setpts=PTS-STARTPTS[v0];[0:a]atrim=start={a}:end={b},asetpts=PTS-STARTPTS[a0];[0:v]trim=start={c}:end={d},setpts=PTS-STARTPTS[v1];[0:a]atrim=start={c}:end={d},asetpts=PTS-STARTPTS[a1];[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]'
assert not out.exists()
subprocess.run(['ffmpeg','-v','error','-n','-i',str(movie),'-filter_complex',graph,'-map','[v]','-map','[a]','-c:v','libx264','-preset','fast','-crf','18','-threads','4','-c:a','aac','-b:a','256k','-ar','48000','-r','30','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],check=True)
subprocess.run(['ffmpeg','-v','error','-i',str(out),'-f','null','-'],check=True,capture_output=True)
(V/'qa/v14/preview.json').write_text(json.dumps({'file':str(out.relative_to(V)),'sourceRangesSeconds':[[a,b],[c,d]],'decodeComplete':True,'purpose':'Focused proof of Evergreen entrance, platform spacing, large tree and closing logo growth.'},indent=2)+'\n');print(out.name)
