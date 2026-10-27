"""V3 internal-review verification: native frames, all-frame caption bounds, copied AAC."""
from pathlib import Path
import hashlib,json,math,subprocess,re
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];Q=R/'qa/us-v1-60s-v3'
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def cmd(a): return subprocess.check_output(a)
def load(p): return json.loads(p.read_text())
def rgb(p): return np.array(Image.open(p).convert('RGB'))
def packet_data(p):
    d=json.loads(cmd(['ffprobe','-v','error','-select_streams','a:0','-show_packets','-show_data_hash','sha256','-show_entries','packet=pts,dts,duration,data_hash','-of','json',str(p)]))
    return d['packets']
def pcm(p): return cmd(['ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-f','f32le','-'])
def main():
    base=load(Q/'baseline.json');changed=[p for p,h in base.items() if digest(R/p)!=h]
    assert changed==['src/Root.tsx'],changed
    root=(R/'src/Root.tsx').read_text()
    restored=re.sub(r"^import \{USFilm60V3\}.*\n",'',root)
    restored=re.sub(r'<Composition id="US-Team-v1-60s-V3".*?/>','',restored)
    assert restored==(Q/'source/Root-before.tsx').read_text()
    t=load(Q/'timeline.json');v2=load(R/'src/config/us-full-v2-timeline.json')
    clone=json.loads(json.dumps(t))
    for s in clone['scenes']: s.pop('subtitleCues')
    assert clone==v2,'Only subtitleCues may differ from V2 timeline'
    cues=[]
    for s in t['scenes']:
        assert 1<=len(s['subtitleCues'])<=3
        for c in s['subtitleCues']:
            c=dict(c);c['scene']=s['id'];c['from']=s['voiceStartFrame']+math.ceil(s['words'][c['startWord']]['start']*30);c['to']=min(s['endFrame'],s['voiceStartFrame']+math.ceil(s['words'][c['endWord']]['end']*30));cues.append(c)
        assert ' '.join(c['en'] for c in s['subtitleCues'])==s['text'],s['id']
    audits=list(load(Q/'frame-audit.json').values());audits.sort(key=lambda a:a['frame'])
    assert [a['frame'] for a in audits]==list(range(1800))
    safety={s['id']:{'captionTop':1080.,'contentBottom':0.,'visibleCaptionFrames':0} for s in t['scenes']}
    for a in audits:
        f=a['frame'];c=next((c for c in cues if c['from']<=f<c['to']),None)
        cap=[x for x in a['text'] if x.get('caption')]
        assert len(cap)==(2 if c else 0),(f,c,cap)
        if c:
            assert [x['text'] for x in cap]==[c['en'],c['zh']],(f,cap)
            assert [x['fontSize'] for x in cap]==['28px','22px'],(f,cap)
            top=min(x['y'] for x in cap);bottom=max(x['y']+x['height'] for x in cap)
            assert top>=880 and bottom<=1016.1,(f,top,bottom)
            safety[a['scene']]['captionTop']=min(safety[a['scene']]['captionTop'],top)
            safety[a['scene']]['visibleCaptionFrames']+=1
        for x in a['text']:
            assert x['x']>=-.01 and x['y']>=-.01 and x['x']+x['width']<=1920.01 and x['y']+x['height']<=1080.01,(f,x)
            if not x.get('caption') and 'Internal review' not in x['text']:
                safety[a['scene']]['contentBottom']=max(safety[a['scene']]['contentBottom'],x['y']+x['height'])
    # Conservative outer bounds include row/cell whitespace and their maximum
    # animated Y displacement; this also covers rules absent from text metrics.
    for sid,bound in [('S3',894),('S5',910)]:
        safety[sid]['textBottom']=safety[sid]['contentBottom']
        safety[sid]['contentBottom']=max(safety[sid]['contentBottom'],bound)
    safety['S7']['contentBottom']=max(safety['S7']['contentBottom'],644)
    for sid,values in safety.items():
        values['gap']=values['captionTop']-values['contentBottom']
        if sid in ['S3','S4','S5']: assert values['gap']>0,(sid,values)
    teamA=rgb(Q/'frames/team-no-captions-f120.png');teamB=rgb(Q/'frames/team-v2-f120.png')
    assert np.array_equal(teamA,teamB),'No-caption native team must be exactly the unchanged V2 team'
    reference=rgb(Q/'frames/official-reference.png');actual=rgb(Q/'frames/final-logo.png')
    opaque=reference[:,:,0]==0
    assert np.array_equal(reference[opaque],actual[opaque]),'Official opaque foreground must match exact PNG colors'
    samples=[]
    for color in ['#004098','#0051a4','#007bc7','#0093d0']:
        v=tuple(bytes.fromhex(color[1:]));m=np.all(reference==v,axis=2);m[:,800:]=False
        ys,xs=np.where(m);assert len(xs)>0;i=len(xs)//2;x,y=int(xs[i]),int(ys[i])
        assert np.array_equal(reference[y,x],actual[y,x])
        samples.append(dict(color=color,x=x,y=y,rgb=actual[y,x].tolist(),count=int(np.all(actual==v,axis=2).sum())))
    for part,x,y in [('trunk',640,605),('leaf',638,475),('base',640,638)]:
        assert np.array_equal(reference[y,x],actual[y,x]);samples.append(dict(part=part,x=x,y=y,rgb=actual[y,x].tolist()))
    (Q/'logo-colors.json').write_text(json.dumps(dict(samples=samples,opaqueReferencePixels=int(opaque.sum()),opaqueChangedPixels=0),indent=2))
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',21)
    canvas=Image.new('RGB',(1920,1310),'#f7f4ee');canvas.paste(Image.fromarray(actual),(0,0));draw=ImageDraw.Draw(canvas)
    for i,p in enumerate(samples[:4]):
        x,y=p['x'],p['y'];draw.ellipse((x-10,y-10,x+10,y+10),outline='#d65831',width=2);draw.text((x+13,y-20),str(i+1),font=font,fill='#b54828')
        bx=45+i*470;draw.rectangle((bx,1120,bx+65,1185),fill=p['color']);draw.text((bx+85,1125),f"{i+1}. {p['color']}  ({x}, {y})",font=font,fill='#222222');draw.text((bx+85,1160),f"PNG RGB {tuple(p['rgb'])}",font=font,fill='#222222')
    draw.text((45,1230),f"Official SVG opaque foreground: {int(opaque.sum())} pixels; changed pixels: 0. Native PNG only, not H.264 pixel parity.",font=font,fill='#222222')
    canvas.save(Q/'logo-color-check.png')
    assert np.array_equal(rgb(Q/'logo-growth-frames/local-4.20s.png'),actual),'Final hold must be static from local 4.2s'
    # Native ink clearance is more useful than overlapping font line boxes on S2.
    teamCap=rgb(Q/'frames/S2-cue2.png');m=np.any(teamCap!=teamA,axis=2);ys,xs=np.where(m)
    caption_ink_top=int(ys.min());content=teamA[:caption_ink_top];bg=teamA[0,0];cy,cx=np.where(np.any(content!=bg,axis=2));content_ink_bottom=int(cy.max())
    safety['S2']['nativeInkTop']=caption_ink_top;safety['S2']['nativeContentInkBottom']=content_ink_bottom;safety['S2']['nativeInkGap']=caption_ink_top-content_ink_bottom-1
    assert safety['S2']['nativeInkGap']>=2,safety['S2']
    rows=['# 双语字幕安全区逐帧核验','', '1080p 坐标；1800 帧审计。字幕 bottom=64，无背景；全片最高点≥880。内容底点以正文 line box 为准；S3/S5另用含分隔线、留白和最大入场位移的保守整块外框上界。S7计入Logo向量底点644px，忽略底部内部审片脚注。','', '| 段 | 字幕最高点 | 内容最低点 | line box 间隔 | 有字幕帧 |','|---|---:|---:|---:|---:|']
    for sid,v in safety.items(): rows.append(f"| {sid} | {v['captionTop']:.2f} | {v['contentBottom']:.2f} | {v['gap']:.2f} | {v['visibleCaptionFrames']} |")
    rows+=['',f"S2 的既有经历文字和字幕 line box 有 {max(0,-safety['S2']['gap']):.2f}px 交叠；原生PNG实际字形互不遮挡，经历末像素 y={content_ink_bottom}，字幕首像素 y={caption_ink_top}，其间 {safety['S2']['nativeInkGap']} 行空白。为保持已通过人物镜，未移动原布局。其余正文保持原V2，S3/S4/S5均有正安全间隔。",'', '18条cue按已有词对齐向上取整；英中共用起止帧，保留标点对应的句间停顿。S5前两句合为一条cue。参考词对齐来自既有V2，并非新增人工语音认证。']
    (Q/'caption-safety.md').write_text('\n'.join(rows)+'\n')
    def stamp(f):
        ms=round(f/30*1000);return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}'
    for language in ['bilingual','en','zh']:
        lines=[]
        for i,c in enumerate(cues):
            text=c['en']+'\n'+c['zh'] if language=='bilingual' else c[language]
            lines.append(f"{i+1}\n{stamp(c['from'])} --> {stamp(c['to'])}\n{text}\n")
        (Q/f'subtitles-{language}.srt').write_text('\n'.join(lines))
    src=R/'out/US-Team-v1_60s_內容版.mp4';packets=packet_data(src);sourcePCM=pcm(src);reports=[]
    for name in ['US-Team-v1_60s_雙語字幕版.mp4','US-Team-v1_60s_雙語字幕版_無字幕.mp4']:
        p=R/'out'/name
        info=json.loads(cmd(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(p)]))
        video=next(s for s in info['streams'] if s['codec_type']=='video')
        assert video['width']==1920 and video['height']==1080 and video['nb_read_frames']=='1800' and video['avg_frame_rate']=='30/1'
        assert float(video['duration'])==60
        assert packet_data(p)==packets,'AAC hashes and timestamps must match V2'
        assert pcm(p)==sourcePCM,'Decoded PCM must match V2 exactly'
        subprocess.run(['ffmpeg','-v','error','-i',str(p),'-f','null','-'],check=True)
        reports.append(dict(file=name,sha256=digest(p),videoFrames=1800,duration=60,aacPackets=len(packets),aacPacketAndTimestampsIdentical=True,decodedPCMIdentical=True))
    # The clean video's caption area is plain paper throughout all 1800 frames.
    clean=R/'out/US-Team-v1_60s_雙語字幕版_無字幕.mp4'
    process=subprocess.Popen(['ffmpeg','-v','error','-i',str(clean),'-vf','crop=1200:70:360:946,format=gray','-f','rawvideo','-'],stdout=subprocess.PIPE)
    count=0;maxStd=0
    while True:
        data=process.stdout.read(1200*70)
        if not data:break
        assert len(data)==1200*70
        value=float(np.frombuffer(data,dtype=np.uint8).std());maxStd=max(maxStd,value);count+=1
    assert process.wait()==0 and count==1800
    assert maxStd<2,('Captions/content found in clean caption area',maxStd)
    (Q/'clean-caption-area.json').write_text(json.dumps(dict(frames=count,region=[360,946,1200,70],maxGrayStd=maxStd,threshold=2,passed=True),indent=2))
    # Exact audio and native visuals checks are independent of lossy codec colour changes.
    result=dict(protectedBaseline=len(base),unchanged=len(base)-1,rootOnlyAppend=True,captionCues=len(cues),auditedFrames=len(audits),cleanCaptionRegionFrames=count,cleanCaptionMaxStd=maxStd,captionSafety=safety,nativeTeamChangedPixels=0,officialOpaqueLogoChangedPixels=0,outputs=reports)
    (Q/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
