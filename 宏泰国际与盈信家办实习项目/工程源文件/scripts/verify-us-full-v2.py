"""Post-render internal-review QA. Run only once all V2 render inputs exist."""
from pathlib import Path
import hashlib, json, math, re, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

R = Path(__file__).resolve().parents[1]
Q = R / 'qa/us-v1-60s-v2'
VIDEO = R / 'out/US-Team-v1_60s_內容版.mp4'
MASTER = R / 'public/music/us-v2/full-review-mix.wav'
CJK = re.compile('[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\u3000-\u303f\uff00-\uffef]')

def command(args):
    return subprocess.check_output(args)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def pcm(path):
    return np.frombuffer(command(['ffmpeg','-v','error','-i',str(path),'-ar','48000','-ac','2','-f','f32le','-']), np.float32)

def normalize_word(word):
    return re.sub('[^a-z0-9]', '', word.lower())

def main():
    needed = [Q/'timeline.json', Q/'baseline.json', Q/'source/Root-before.tsx', Q/'frame-audit.json', VIDEO, MASTER,
              Q/'frames/team-full-f120.png', Q/'frames/team-reference-f120.png']
    missing = [str(p) for p in needed if not p.exists()]
    if missing:
        raise SystemExit('Inputs not ready:\n'+'\n'.join(missing))
    timeline = json.loads((Q/'timeline.json').read_text())
    fps = timeline.get('fps', 30)
    count = timeline.get('frames', round(timeline['duration']*fps))
    scenes = timeline['scenes']
    assert fps == 30 and count == 1800
    assert scenes[0]['startFrame'] == 0 and scenes[-1]['endFrame'] == count
    for i, scene in enumerate(scenes):
        assert scene.get('playbackRate', 1) == 1, scene['id']
        assert scene['startFrame'] < scene['endFrame']
        if i: assert scenes[i-1]['endFrame'] == scene['startFrame']
        assert scene['voiceStartFrame'] >= scene['startFrame']
        assert scene['voiceStartFrame']/fps + scene['duration'] <= scene['endFrame']/fps + 1e-6, scene['id']
    raw = json.loads((Q/'frame-audit.json').read_text())
    audits = list(raw.values()) if isinstance(raw, dict) else raw
    audits.sort(key=lambda a:a['frame'])
    assert len(audits) == count and [a['frame'] for a in audits] == list(range(count))
    bound_errors, cjk_errors = [], []
    for audit in audits:
        f = audit['frame']
        expected = next(s['id'] for s in scenes if s['startFrame'] <= f < s['endFrame'])
        assert audit['scene'] == expected and audit['playbackRate'] == 1, f
        assert 'text' in audit, f
        for item in audit['text']:
            text = item.get('text','').strip()
            if not text or float(item.get('opacity',1)) <= .01: continue
            if CJK.search(text): cjk_errors.append({'frame':f,'text':text})
            x,y,w,h = (float(item[k]) for k in ('x','y','width','height'))
            if x < -1 or y < -1 or x+w > 1921 or y+h > 1081:
                bound_errors.append({'frame':f,**item})
    assert not cjk_errors, cjk_errors[:5]
    assert not bound_errors, bound_errors[:5]

    # Find cue starts from the synthesized word alignments, not guessed wall times.
    gates = [('S1', r'\b1997\b', 'nineteen'), ('S3', r'\b10\s*B\+?', 'ten'),
             ('S3', r'\b1\.5\s*B\+?', 'one'), ('S3', r'\b3\b', 'three'),
             ('S4', r'\b(?:9|Nine)\b', 'nine'), ('S4', r'\b(?:100|century|hundred)', 'hundred')]
    gate_results = []
    for scene_id, pattern, word in gates:
        scene = next(s for s in scenes if s['id']==scene_id)
        match_words = [w for w in scene['words'] if normalize_word(w['word'])==word]
        if not match_words and word=='hundred':
            match_words = [w for w in scene['words'] if normalize_word(w['word']).startswith('century')]
        assert match_words, f'Missing word alignment: {scene_id}/{word}'
        cue = scene['voiceStartFrame'] + math.ceil(float(match_words[0]['start'])*fps-1e-9)
        matching = [a['frame'] for a in audits if a['scene']==scene_id and any(
            re.search(pattern,t.get('text',''),re.I) and float(t.get('opacity',1))>.01 for t in a['text'])]
        assert matching, f'Text gate not observed: {scene_id}/{pattern}'
        assert min(matching) >= cue, f'{scene_id} {pattern}: text {min(matching)} precedes speech {cue}'
        gate_results.append({'scene':scene_id,'textPattern':pattern,'word':match_words[0]['word'].strip(),
                             'wordStartFrame':cue,'firstVisibleFrame':min(matching)})

    baseline = json.loads((Q/'baseline.json').read_text())
    missing_old = [p for p in baseline if not (R.parent/p).exists()]
    assert not missing_old, missing_old
    changed = [p for p,h in baseline.items() if digest(R.parent/p)!=h]
    assert set(changed)=={'video/src/Root.tsx'}, changed
    root = (R/'src/Root.tsx').read_text()
    root, ni = re.subn(r'^import\s*\{\s*USFilm60V2\s*\}\s*from\s*[\'\"]\./scenes/USFilm60V2[\'\"];?\n', '', root, flags=re.M)
    root, nc = re.subn(r'<Composition\b(?=[^>]*\bid=[\'\"]US-Team-v1-60s-V2[\'\"])[\s\S]*?/>', '', root)
    assert ni == nc == 1, (ni,nc)
    assert root == (Q/'source/Root-before.tsx').read_text(), 'Root changed beyond V2 import/composition'
    x,y = (np.array(Image.open(Q/f'frames/{name}').convert('RGB')) for name in ['team-full-f120.png','team-reference-f120.png'])
    assert x.shape==y.shape and np.array_equal(x[:1000],y[:1000]), 'Team native image changed'
    assert (R/'public/vo/us-v2/S2.wav').read_bytes()==(R/'public/vo/us-v1/team-b/VO-01.wav').read_bytes()
    people = json.loads((R/'src/config/us-team-v1.json').read_text())
    assert len(people)==6 and max(p['scale'] for p in people)<=1

    subprocess.run(['ffmpeg','-v','error','-i',str(VIDEO),'-f','null','-'],check=True)
    probe = json.loads(command(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(VIDEO)]))
    v = next(s for s in probe['streams'] if s['codec_type']=='video')
    assert v['width']==1920 and v['height']==1080 and int(v.get('nb_read_frames',v.get('nb_frames',0)))==count
    assert abs(float(probe['format']['duration'])-count/fps)<.05
    assert v['r_frame_rate']=='30/1'
    a,b = pcm(VIDEO),pcm(MASTER)
    assert abs(len(a)-len(b))<=2048*2, (len(a),len(b))
    n=min(len(a),len(b)); corr=float(np.corrcoef(a[:n],b[:n])[0,1]); assert corr>.999, corr
    log=subprocess.run(['ffmpeg','-hide_banner','-i',str(VIDEO),'-vn','-af','loudnorm=I=-16:TP=-1:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True).stderr
    loud=json.JSONDecoder().raw_decode(log[log.rindex('{'):])[0]
    assert float(loud['input_tp'])<=-1, loud

    # Each screenshot comes from the actual encoded deliverable. Pick late frames for dense scenes.
    sheet=Image.new('RGB',(1280,400*math.ceil(len(scenes)/2)),'#e9e5df')
    draw=ImageDraw.Draw(sheet); font=ImageFont.truetype(str(R/'public/fonts/Geist.ttf'),20)
    selected=[]
    for i,s in enumerate(scenes):
        progress=.88 if s['id'] in ['S3','S4','S7'] else .7
        frame=s['startFrame']+min(s['endFrame']-s['startFrame']-12,round((s['endFrame']-s['startFrame'])*progress))
        file=Q/f"frames/actual-{s['id']}.png"
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(VIDEO),'-vf',f'select=eq(n\\,{frame})','-frames:v','1',str(file)],check=True)
        im=Image.open(file).convert('RGB'); im.thumbnail((624,351)); cx=i%2*640; cy=i//2*400
        sheet.paste(im,(cx,cy+32)); draw.text((cx+12,cy+4),f"{s['id']} / {frame/fps:.2f}s",fill='#24211f',font=font)
        selected.append({'scene':s['id'],'frame':frame,'file':str(file.relative_to(R))})
    sheet.save(Q/'actual-storyboard.jpg',quality=94)
    report={'status':'technical_checks_passed_visual_and_user_review_separate', 'duration':count/fps,'frames':count,'fps':fps,
      'fullDecodePassed':True,'auditedFrames':len(audits),'noVisibleCJK':True,'visibleTextWithinFrame':True,
      'textOverlapCheck':'Not inferred from DOM block rectangles; actual storyboard and large frames require visual review. Block rectangles do not establish glyph ink overlap.',
      'numericGates':gate_results,'protectedFiles':len(baseline),'changedProtectedFiles':changed,'rootOnlyAdditive':True,
      'allOldProtectedFilesExceptRootUnchanged':True,'teamNativeYBelow1000Identical':True,'S2AudioByteIdentical':True,
      'allPortraitScalesAtMost1':True,'finalAudioMasterCorrelation':corr,'loudnessLUFS':loud['input_i'],
      'truePeakDBTP':loud['input_tp'],'storyboardFrames':selected,'releaseStatus':'internal_review_only', 'sha256':digest(VIDEO)}
    (Q/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    main()
