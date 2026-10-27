"""V5: unchanged sources, exact focus sequence, captions, score and encoded audio."""
from pathlib import Path
import json,math,re,hashlib,subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];Q=R/'qa/us-v1-60s-v5';VIDEO=R/'out/US-Team-v1_60s_配樂與人物版.mp4';SR=48000

def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def command(args):return subprocess.check_output(args)
def pcm(p):return np.frombuffer(command(['ffmpeg','-v','error','-i',str(p),'-ar','48000','-ac','2','-f','f32le','-']),np.float32).reshape(-1,2)
def rms(a):return float(np.sqrt(np.mean(np.asarray(a,dtype=np.float64)**2)))
def db(x):return float(20*np.log10(max(float(x),1e-12)))
def rgb(p):return np.asarray(Image.open(p).convert('RGB'))
def band(data):
    mono=data.mean(axis=1);window=np.hanning(SR);freq=np.fft.rfftfreq(SR,1/SR);select=(freq>=40)&(freq<=50);vals=[]
    for i in range(0,len(mono)-SR+1,SR//2):
        f=np.fft.rfft(mono[i:i+SR]*window);vals.append(float(np.sum(np.abs(f[select])**2)/np.sum(window**2)/SR))
    return float(np.mean(vals))
def main():
    needed=[Q/'frame-audit.json',VIDEO,Q/'music/analysis.json',Q/'preserved-native-checks.json']
    assert all(p.exists() for p in needed),[str(p) for p in needed if not p.exists()]
    baseline=load(Q/'baseline.json');changed=[p for p,h in baseline.items() if sha(R/p)!=h]
    assert set(changed)=={'src/Root.tsx','public/music/us-v2/ASSET_ROLES.json'},changed
    roles=load(R/'public/music/us-v2/ASSET_ROLES.json');historical=load(Q/'source/ASSET_ROLES-before.json')
    assert {k:v for k,v in roles.items() if k!='scoreV2'}==historical,'Historical music/mix keys unchanged'
    root=(R/'src/Root.tsx').read_text();restored=re.sub(r"^import \{USFilm60V5\}.*\n",'',root);restored=re.sub(r'<Composition id="US-Team-v1-60s-V5".*?/>','',restored)
    assert restored==(Q/'source/Root-before.tsx').read_text()
    assert (Q/'timeline.json').read_bytes()==(R/'src/config/us-full-v3-timeline.json').read_bytes()
    native=load(Q/'preserved-native-checks.json');assert len(native)==19 and all(n['changedPixels']==0 for n in native)
    t=load(Q/'timeline.json');cues=[]
    for s in t['scenes']:
        for c in s['subtitleCues']:
            cues.append(dict(en=c['en'],zh=c['zh'],start=s['voiceStartFrame']+math.ceil(s['words'][c['startWord']]['start']*30),end=s['voiceStartFrame']+math.ceil(s['words'][c['endWord']]['end']*30)))
    records=list(load(Q/'frame-audit.json').values());records.sort(key=lambda a:a['frame']);assert [a['frame'] for a in records]==list(range(1800))
    ranges=[(12,48),(48,84),(84,120),(120,156),(156,192),(192,222)]
    people=load(R/'src/config/us-team-v1.json');achievements=load(R/'src/config/us-team-achievements-v5.json')
    assert len(achievements)==6 and all(a['status']=='pending_verification' and a['sourcePage']==19 and len(a['lines'])<=2 for a in achievements)
    focusCounts={p['slug']:0 for p in people};s2Frames=0;completedChars={};blockGap=1080
    for a in records:
        f=a['frame'];expected=next((c for c in cues if c['start']<=f<c['end']),None);caps=[x for x in a['text'] if x.get('caption')]
        assert len(caps)==(2 if expected else 0),(f,caps)
        if expected:
            assert [x['text'] for x in caps]==[expected['en'],expected['zh']] and [x['fontSize'] for x in caps]==['28px','22px']
        for x in a['text']:
            assert x['x']>=-.01 and x['y']>=-.01 and x['x']+x['width']<=1920.1 and x['y']+x['height']<=1080.1,(f,x)
        if a['scene']=='S2':
            s2Frames+=1;local=f-363;active=next((i for i,(lo,hi) in enumerate(ranges) if lo<=local<hi),-1);cards=a['focusCards'];assert len(cards)==6
            assert [c['slug'] for c in cards]==[p['slug'] for p in people]
            selected=[c for c in cards if c['selected']];assert len(selected)==(1 if active>=0 else 0)
            for i,c in enumerate(cards):
                assert 1-1e-8<=c['scale']<=1.04000001
                assert abs(c['x']-(584+i%3*264))<.01
                if local>=12:assert abs(c['y']-(208+i//3*376+(16 if i%3==1 else 0)))<.01
                if active>=0:assert abs(c['opacity']-(1 if i==active else .35))<1e-8,(f,c)
            if active>=0:
                slug=people[active]['slug'];assert selected[0]['slug']==slug and a.get('activePerson')==slug
                focusCounts[slug]+=1
                assert len(a['chars'])==sum(len(line) for line in achievements[active]['lines'])
                assert all(a['chars'][i]>=a['chars'][i+1]-1e-8 for i in range(len(a['chars'])-1)),(f,a['chars'])
                if all(c==1 for c in a['chars']):completedChars.setdefault(slug,local)
                lines=[x for x in a['text'] if x['text'] in achievements[active]['lines']]
                assert len(lines)==2 and all(x['fontSize']=='13px' for x in lines)
            else:assert not a.get('activePerson') and not a['chars']
            for b in a['blocks']:
                if b['id']=='selected-experience' and caps:
                    gap=min(c['y'] for c in caps)-(b['y']+b['height']);assert gap>0;blockGap=min(blockGap,gap)
    assert s2Frames==240 and list(focusCounts.values())==[36,36,36,36,36,30]
    assert len(completedChars)==6
    for i,p in enumerate(people):assert completedChars[p['slug']]<ranges[i][1]
    # Tree-only icon retains all source colours and finishes at local 1.6s.
    crop=lambda p:rgb(p)[150:222,256:344]
    assert np.array_equal(crop(Q/'s1-logo-frames/local-1.6s.png'),crop(Q/'frames/S1-v5.png'))
    colors=load(Q/'s1-color-check.json');assert all(colors.values())
    im0=crop(Q/'s1-logo-frames/local-0.0s.png');assert np.all(im0==im0[0,0]),'No fully drawn/faded tree at start'
    # Exact VO bus preserved; 24-bit mix is the sum of that unchanged voice and music.
    assert sha(Q/'music/voice-bus.wav')==sha(R/'qa/us-v1-60s-v2/voice-bus.wav')
    voice=pcm(Q/'music/voice-bus.wav');music=pcm(Q/'music/music-bus.wav');mix=pcm(R/'public/music/us-v2/full-review-mix-v5.wav')
    assert len(voice)==len(music)==len(mix)==60*SR
    sumError=float(np.max(np.abs(mix-(voice+music))));assert sumError<3e-7,sumError
    assert np.max(np.abs(music[:4*SR]))==0
    s6a=t['scenes'][6]['startFrame']*1600;s6b=t['scenes'][6]['endFrame']*1600;assert np.max(np.abs(music[s6a:s6b]))==0
    analysis=load(Q/'music/analysis.json');assert analysis['polyphonyMeanFull60s']>=3 and len(analysis['melodyDurations'])>=3
    poly=np.load(Q/'music/polyphony.npy');assert abs(float(poly.mean())-analysis['polyphonyMeanFull60s'])<1e-8
    actualBandGain=10*np.log10(band(music)/band(pcm(R/'qa/us-v1-60s-v2/music-bus.wav')));assert actualBandGain>=6
    s3=t['scenes'][3];s5=t['scenes'][5];gap=20*np.log10(rms(music[s3['startFrame']*1600:s3['endFrame']*1600])/rms(music[s5['startFrame']*1600:s5['endFrame']*1600]));assert gap>=5
    peakGap=db(np.max(np.abs(voice)))-db(np.max(np.abs(music)));assert peakGap>=12
    assert db(np.max(np.abs(mix)))<=-1
    probe=json.loads(command(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(VIDEO)]))
    v=next(s for s in probe['streams'] if s['codec_type']=='video');assert (v['width'],v['height'],v['avg_frame_rate'],v['nb_read_frames'])==(1920,1080,'30/1','1800') and float(v['duration'])==60
    subprocess.run(['ffmpeg','-v','error','-i',str(VIDEO),'-f','null','-'],check=True)
    encoded=pcm(VIDEO);count=min(len(encoded),len(mix));corr=float(np.corrcoef(encoded[:count].ravel(),mix[:count].ravel())[0,1]);assert corr>.999
    loud=subprocess.run(['ffmpeg','-hide_banner','-i',str(VIDEO),'-af','loudnorm=I=-16:TP=-1:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
    loudness=json.JSONDecoder().raw_decode(loud.stderr[loud.stderr.rfind('{'):])[0];assert float(loudness['input_tp'])<=-1
    (Q/'music/encoded-loudness.json').write_text(json.dumps(loudness,indent=2)+'\n')
    # Actual coded-frame storyboard, distinct from lossless native QA frames.
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',19);board=Image.new('RGB',(1280,4*392),'#f7f4ee');draw=ImageDraw.Draw(board)
    for i,(sid,f) in enumerate([('S0',50),('S1',324),('S2',443),('S3',876),('S4',1110),('S5',1417),('S6',1529),('S7',1769)]):
        p=Q/'actual'/f'{sid}-f{f}.png';subprocess.run(['ffmpeg','-v','error','-i',str(VIDEO),'-vf',f'select=eq(n\\,{f})','-frames:v','1','-update','1','-y',str(p)],check=True)
        x=i%2*640;y=i//2*392;board.paste(Image.open(p).convert('RGB').resize((640,360)),(x,y));draw.text((x+14,y+365),f'{sid} / frame {f} / {f/30:.2f}s',font=font,fill='#3d3833')
    board.save(Q/'actual-storyboard.jpg',quality=95)
    report=dict(protectedBaseline=len(baseline),unchanged=len(baseline)-2,rootOnlyAppend=True,historicalAssetRolesPreserved=True,allVOFileHashesUnchanged=True,voiceBusByteIdentical=True,mixSumError=sumError,timelineAndCaptionCuesUnchanged=True,auditedFrames=1800,focusSceneFrames=s2Frames,focusCounts=focusCounts,allCharactersCompleteByLocalFrame=completedChars,achievementCaptionMinGap=blockGap,achievementStatus='pending_verification; source PDF p19 matched, external use not approved',nativePreservedFrameCount=len(native),nativePreservedChangedPixels=0,introBluePixels=colors,introCompleteSeconds=1.6,scoreVoicesMean=analysis['polyphonyMeanFull60s'],bass40to50GainDB=actualBandGain,S3minusS5RMSDB=gap,globalVoiceMusicPeakGapDB=peakGap,mixPeakDBFS=db(np.max(np.abs(mix))),encodedTruePeakDBTP=float(loudness['input_tp']),encodedLUFS=float(loudness['input_i']),encodedMasterCorrelation=corr,outputFrames=1800,outputDuration=60,outputSha256=sha(VIDEO))
    (Q/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
