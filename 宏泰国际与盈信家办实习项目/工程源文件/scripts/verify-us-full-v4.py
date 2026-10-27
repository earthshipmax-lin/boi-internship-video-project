"""Prompt17 verification: source identity, all-frame layout, timing, and copied audio."""
from pathlib import Path
import hashlib,json,math,re,subprocess
import numpy as np
from PIL import Image,ImageOps,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];Q=R/'qa/us-v1-60s-v4';VIDEO=R/'out/US-Team-v1_60s_證據版.mp4';OLD=R/'out/US-Team-v1_60s_雙語字幕版.mp4'
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def command(args):return subprocess.check_output(args)
def rgb(p):return np.array(Image.open(p).convert('RGB'))
def packets(p):
    return json.loads(command(['ffprobe','-v','error','-select_streams','a:0','-show_packets','-show_data_hash','sha256','-show_entries','packet=pts,dts,duration,data_hash','-of','json',str(p)]))['packets']
def pcm(p):return command(['ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-f','f32le','-'])
def normalize(word):return re.sub('[^a-z0-9]','',word.lower())
def main():
    required=['baseline.json','source/Root-before.tsx','timeline.json','frame-audit.json','assets/manifest.json','preserved-native-checks.json']
    missing=[str(Q/f) for f in required if not (Q/f).exists()]
    if not VIDEO.exists():missing.append(str(VIDEO))
    if missing:raise SystemExit('Inputs not ready: '+', '.join(missing))
    baseline=load(Q/'baseline.json');changed=[p for p,h in baseline.items() if sha(R/p)!=h]
    assert changed==['src/Root.tsx'],changed
    root=(R/'src/Root.tsx').read_text();restored=re.sub(r"^import \{USFilm60V4\}.*\n",'',root);restored=re.sub(r'<Composition id="US-Team-v1-60s-V4".*?/>','',restored)
    assert restored==(Q/'source/Root-before.tsx').read_text(),'Old compositions must be unchanged'
    assert (Q/'timeline.json').read_bytes()==(R/'src/config/us-full-v3-timeline.json').read_bytes(),'Full timeline, VO alignment and subtitle cues frozen'
    native=load(Q/'preserved-native-checks.json');assert len(native)==14 and all(x['changedPixels']==0 for x in native)
    # Source copies, exact grade, and conservative cover scale for every placement.
    manifest=load(Q/'assets/manifest.json');assert len(manifest['assets'])==9 and len(manifest['placements'])==5
    for a in manifest['assets']:
        assert sha(R/'public'/a['file'])==a['sha256']
        assert list(Image.open(R/'public'/a['file']).size)==a['size']
        if a['used']:
            assert sha(R/'public'/a['gradedFile'])==a['gradedSha256']
            assert list(Image.open(R/'public'/a['gradedFile']).size)==a['size'],'No interpolated asset enlargement'
    maxScale=0
    for p in manifest['placements']:
        scale=max(p['width']/p['nativeSize'][0],p['height']/p['nativeSize'][1]);assert scale==p['scale'] and scale<=1
        maxScale=max(maxScale,scale)
    t=load(Q/'timeline.json');scenes=t['scenes'];cues=[]
    for s in scenes:
        for c in s['subtitleCues']:
            cues.append(dict(scene=s['id'],en=c['en'],zh=c['zh'],start=s['voiceStartFrame']+math.ceil(s['words'][c['startWord']]['start']*30),end=s['voiceStartFrame']+math.ceil(s['words'][c['endWord']]['end']*30)))
    records=list(load(Q/'frame-audit.json').values());records.sort(key=lambda a:a['frame'])
    assert [a['frame'] for a in records]==list(range(1800))
    changedScenes=['S1','S3','S4','S5'];gaps={sid:float('inf') for sid in changedScenes};tops={sid:1080. for sid in changedScenes};bottoms={sid:0. for sid in changedScenes};boxChecks=0
    photoFirst={};photoFull={};photoComplete={};allFigureCaptions={};firstStats={};captionFrames=0
    for a in records:
        f=a['frame'];s=next(s for s in scenes if s['startFrame']<=f<s['endFrame']);assert s['id']==a['scene'] and a['playbackRate']==1
        expected=next((c for c in cues if c['start']<=f<c['end']),None)
        caps=[x for x in a['text'] if x.get('caption')]
        assert len(caps)==(2 if expected else 0),(f,caps)
        if expected:
            assert [x['text'] for x in caps]==[expected['en'],expected['zh']],(f,caps)
            assert [x['fontSize'] for x in caps]==['28px','22px']
            assert min(x['y'] for x in caps)>=880 and max(x['y']+x['height'] for x in caps)<=1016.1
            captionFrames+=1
        for x in a['text']:
            assert x['x']>=-.1 and x['y']>=-.1 and x['x']+x['width']<=1920.1 and x['y']+x['height']<=1080.1,(f,x)
            if x['text'].startswith('FIG.'):
                assert x['fontSize']=='14px';allFigureCaptions[x['text']]=True
        for b in a['blocks']:
            assert b['x']>=0 and b['y']>=0 and b['x']+b['width']<=1920.01 and b['y']+b['height']<=938,(f,b)
            if b['photo']:
                assert 0<b['scale']<=1
                photoFirst.setdefault(b['id'],f)
                if b['opacity']>=.9999:photoFull.setdefault(b['id'],f)
                if b['opacity']==1:photoComplete.setdefault(b['id'],f)
            if b['id'].startswith('stat-') or b['id']=='nine-state-register':firstStats.setdefault(b['id'],f)
        if a['scene'] in changedScenes and caps:
            top=min(x['y'] for x in caps)
            body=[x for x in a['text'] if not x.get('caption')]
            bottom=max([x['y']+x['height'] for x in body]+[b['y']+b['height'] for b in a['blocks']]+[0])
            gap=top-bottom;assert gap>=0,(f,gap,bottom)
            gaps[a['scene']]=min(gaps[a['scene']],gap);tops[a['scene']]=min(tops[a['scene']],top);bottoms[a['scene']]=max(bottoms[a['scene']],bottom)
            boxChecks+=len(body)+len(a['blocks'])
    assert len(allFigureCaptions)==5
    assert set(photoFirst)=={'fig01','fig02','fig03','fig04','fig05'}
    assert photoFirst['fig03']-photoFirst['fig02']==8 and photoFirst['fig04']-photoFirst['fig03']==8
    def absoluteCue(sid,word):
        s=next(s for s in scenes if s['id']==sid);w=next(w for w in s['words'] if normalize(w['word'])==word)
        return s['voiceStartFrame']+math.ceil(w['start']*30)
    for sid,word,key in [('S3','ten','stat-ten'),('S3','one','stat-one'),('S3','three','stat-three'),('S4','nine','nine-state-register')]:
        assert firstStats[key]==absoluteCue(sid,word)+1,(key,firstStats[key],absoluteCue(sid,word))
    assert photoComplete['fig04']<absoluteCue('S3','three')
    assert photoFirst['fig01']==120+10 and photoFirst['fig05']==absoluteCue('S5','flushing')+1
    for sid,names in [('S4',['California','New York','Massachusetts','Arizona','Connecticut','Texas','North Carolina','Delaware','New Jersey'])]:
        for name in names:assert any(a['scene']==sid and any(name in x['text'] for x in a['text']) for a in records),name
    # Audio is stream-copied from V3, including packet timing, not regenerated.
    oldPackets=packets(OLD);newPackets=packets(VIDEO);assert oldPackets==newPackets
    assert pcm(OLD)==pcm(VIDEO)
    probe=json.loads(command(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(VIDEO)]))
    v=next(s for s in probe['streams'] if s['codec_type']=='video');assert (v['width'],v['height'],v['avg_frame_rate'],v['nb_read_frames'])==(1920,1080,'30/1','1800') and float(v['duration'])==60
    subprocess.run(['ffmpeg','-v','error','-i',str(VIDEO),'-f','null','-'],check=True)
    # Actual H264 frames are kept separately from native PNG color measurements.
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',20)
    board=Image.new('RGB',(1280,4*392),'#f7f4ee');draw=ImageDraw.Draw(board)
    sampleFrames=[('S0',50),('S1',324),('S2',536),('S3',876),('S4',1110),('S5',1417),('S6',1529),('S7',1769)]
    for i,(sid,f) in enumerate(sampleFrames):
        p=Q/'actual'/f'{sid}-f{f}.png';subprocess.run(['ffmpeg','-v','error','-i',str(VIDEO),'-vf',f'select=eq(n\\,{f})','-frames:v','1','-update','1','-y',str(p)],check=True)
        im=Image.open(p).convert('RGB').resize((640,360));x=i%2*640;y=i//2*392;board.paste(im,(x,y));draw.text((x+16,y+365),f'{sid} / frame {f} / {f/30:.2f}s',font=font,fill='#3d3833')
    board.save(Q/'actual-storyboard.jpg',quality=95)
    safety=['# 新照片、正文与双语字幕安全区','', '1800帧审计，逐帧测量双语字幕与可见文字／照片图注／整块容器。以下间隔为有字幕帧内最小值，包含入场位移及容器留白。','', '| 段 | 字幕最上点 | 正文及照片外框最下点 | 最小间隔 |','|---|---:|---:|---:|']
    for sid in changedScenes:safety.append(f'| {sid} | {tops[sid]:.2f} | {bottoms[sid]:.2f} | {gaps[sid]:.2f} |')
    safety+=['', '未改的S0/S2/S6/S7以14张完整原生PNG对照V3，均零像素差；字幕cue／原声／Logo组件同V3。S2保留上一轮已记录的实际字形5行空白，不重新挪动人物。']
    (Q/'caption-safety.md').write_text('\n'.join(safety)+'\n')
    report=dict(protectedBaseline=len(baseline),unchanged=len(baseline)-1,rootOnlyAppend=True,allTimelineAndSubtitleCuesUnchanged=True,auditedFrames=1800,captionFrames=captionFrames,changedSceneFrames=sum(s['endFrame']-s['startFrame'] for s in scenes if s['id'] in changedScenes),captionLayoutChecks=boxChecks,minCaptionGaps=gaps,photosVisuallyMatched=9,photoPlacements=5,maxPhotoScale=maxScale,figureCaptions=list(allFigureCaptions),photoFirstVisibleFrame=photoFirst,photoFullyVisibleFrame=photoFull,photoNearFullOpacityThreshold=.9999,photoAnimationCompleteFrame=photoComplete,statisticFirstVisibleFrame=firstStats,mapFallback='complete nine-state list; no untraceable map used',preservedNativeComparisons=native,videoFrames=1800,videoDuration=60,aacPackets=len(newPackets),aacPacketsAndTimingIdentical=True,decodedPCMIdentical=True,fullDecodePassed=True,outputSha256=sha(VIDEO),colorGrade='identical explicit Prompt17 transform; no independent calibrated Kelvin certification')
    (Q/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
