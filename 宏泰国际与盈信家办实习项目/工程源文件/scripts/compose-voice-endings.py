"""Compose local narration candidates from a private JSON specification.

Only silence edits, fixed EQ, static loudness matching and a subtle room
impulse response are supported. Source speech is never time-stretched or
pitch-shifted. Media and private specifications stay outside source sync.
"""
from pathlib import Path
import argparse, hashlib, json, math, re, subprocess
import numpy as np
from scipy.signal import fftconvolve, butter, sosfilt
SR = 48000


def pcm(path):
    return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-ar',str(SR),'-ac','2','-f','f32le','-']),dtype='<f4').reshape(-1,2).copy()


def write(path,a):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists(): raise FileExistsError(path)
    subprocess.run(['ffmpeg','-v','error','-n','-f','f32le','-ar',str(SR),'-ac','2','-i','-','-c:a','pcm_s24le',str(path)],input=a.astype('<f4').tobytes(),check=True)


def measure(path):
    r=subprocess.run(['ffmpeg','-hide_banner','-i',str(path),'-af','loudnorm=I=-16:TP=-1.1:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
    return json.loads(re.findall(r'\{\s*"input_i".*?\}',r.stderr,re.S)[-1])


def bounds(a,db=-40):
    e=np.array([np.max(np.abs(a[i:i+480])) for i in range(0,len(a),480)])
    ix=np.where(e>10**(db/20))[0]
    if not len(ix): raise ValueError('No speech detected')
    return int(ix[0]*480),min(len(a),int((ix[-1]+1)*480))


def room_ir(rt60=1.2):
    rng=np.random.default_rng(19);n=round(rt60*SR);ir=np.zeros(n)
    # Dense, diffuse reflections rather than an isolated audible echo.
    indices=rng.integers(round(.023*SR),n,size=2200)
    values=rng.normal(size=len(indices))*np.exp(-math.log(1000)*indices/(SR*rt60))
    np.add.at(ir,indices,values)
    ir=sosfilt(butter(2,4200,fs=SR,output='sos'),ir)
    ir/=np.sqrt(np.sum(ir**2))
    return ir


def prepare(root,work,item):
    src=root/item['source'];a=pcm(src);edits=[]
    for edit in item.get('silenceCuts',[]):
        start,end,target=edit['start'],edit['end'],edit['targetSeconds']
        lo,hi=round(start*SR),round(end*SR);remove=round((end-start-target)*SR);cross=480
        assert remove>cross and float(np.abs(a[lo:hi]).max())<.008
        left=lo+(hi-lo-remove)//2;right=left+remove-cross
        ramp=np.linspace(0,1,cross)[:,None]
        bridge=a[left-cross:left]*(1-ramp)+a[right:right+cross]*ramp
        a=np.concatenate([a[:left-cross],bridge,a[right+cross:]])
        edits.append({'sourceQuietSeconds':[start,end],'targetSeconds':target,'removedSamples':remove,'crossfadeSeconds':.01,'removedRegionPeak':float(np.abs(pcm(src)[lo:hi]).max())})
    raw=work/(item['id']+'-raw.wav');write(raw,a)
    eq=work/(item['id']+'-eq.wav')
    subprocess.run(['ffmpeg','-v','error','-n','-i',str(raw),'-af','highpass=f=80:p=2,equalizer=f=200:t=q:w=0.8:g=1.5','-ar',str(SR),'-c:a','pcm_s24le',str(eq)],check=True)
    gain=10**((-16-float(measure(eq)['input_i']))/20);a=pcm(eq)*gain
    s,e=bounds(a);lo=max(0,s-1920);hi=min(len(a),e+3840)
    clip=a[lo:hi];fade=min(480,len(clip)//5);clip[:fade]*=np.linspace(0,1,fade)[:,None];clip[-fade:]*=np.linspace(1,0,fade)[:,None]
    probe=work/(item['id']+'-trim-probe.wav');write(probe,clip);trim_gain=10**((-16-float(measure(probe)['input_i']))/20);clip*=trim_gain;gain*=trim_gain
    clipped=work/(item['id']+'-clip.wav');write(clipped,clip)
    return clip,{'id':item['id'],'source':item['source'],'sourceSHA256':hashlib.sha256(src.read_bytes()).hexdigest(),'silenceEdits':edits,'eq':['HP80Hz/12dB per octave','bell200Hz Q0.8 +1.5dB'],'staticGain':gain,'trimSourceAfterSilenceEditSamples':[lo,hi],'speechSamples':[s-lo,e-lo],'clipSeconds':len(clip)/SR,'clipLUFS':float(measure(clipped)['input_i']),'nativeTailNote':item.get('nativeTailNote')}


def compose(spec,root):
    work=root/spec['work'];work.mkdir(parents=True,exist_ok=True);prepared={}
    for item in spec['clips']: prepared[item['id']]=prepare(root,work,item)
    reports=[];ir=room_ir(1.2)
    for candidate in spec['candidates']:
        placements=[];cursor=round(spec.get('leadSeconds',.15)*SR)
        for i,name in enumerate(candidate['clips']):
            a,r=prepared[name];s,e=r['speechSamples'];start=cursor-s
            placements.append({'id':name,'clipStart':start,'speechStart':cursor,'speechEnd':start+e})
            cursor=start+e+(round(spec['gapsSeconds'][i]*SR) if i<2 else 0)
        n=placements[-1]['speechEnd']+round(1.2*SR);dry=np.zeros((n,2),np.float64);send=np.zeros_like(dry)
        for i,p in enumerate(placements):
            a,r=prepared[p['id']];lo=p['clipStart'];dry[lo:lo+len(a)]+=a
            if i in [1,2]:
                tail=round((.42 if i==1 else .22)*SR);end=p['speechEnd'];start=max(p['speechStart'],end-tail);mask=np.ones(end-start);k=min(480,len(mask));mask[:k]=np.linspace(0,1,k);send[start:end]+=dry[start:end]*mask[:,None]
        wet=np.column_stack([fftconvolve(send[:,ch],ir)[:n] for ch in range(2)])
        mix=.96*dry+.04*wet;mix[-7200:]*=np.linspace(1,0,7200)[:,None]
        premaster=work/(candidate['id']+'-pre.wav');write(premaster,mix);m=measure(premaster);gain_db=-16-float(m['input_i']);mix*=10**(gain_db/20)
        out=root/candidate['output'];level=work/(candidate['id']+'-level.wav');write(level,mix)
        subprocess.run(['ffmpeg','-v','error','-n','-i',str(level),'-af','alimiter=limit=0.85:attack=5:release=60:level=false:latency=true','-ar',str(SR),'-c:a','pcm_s24le',str(out)],check=True);mix=pcm(out);metrics=measure(out)
        assert -16.5<=float(metrics['input_i'])<=-15.5 and float(metrics['input_tp'])<=-1,(candidate['id'],metrics)
        drypath=work/(candidate['id']+'-dry.wav');write(drypath,dry)
        report={'id':candidate['id'],'file':candidate['output'],'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'seconds':len(mix)/SR,'placements':[{**p,'speechStartSeconds':p['speechStart']/SR,'speechEndSeconds':p['speechEnd']/SR} for p in placements],'interPhraseGapsSeconds':[(b['speechStart']-a['speechEnd'])/SR for a,b in zip(placements,placements[1:])],'staticMasterGainDB':gain_db,'integratedLUFS':float(metrics['input_i']),'truePeakDBTP':float(metrics['input_tp']),'wetFraction':.04,'roomRT60Seconds':1.2,'tailOnlyRoom':True,'noTimeStretch':True,'noPostPitchShift':True,'noCrescendo':True,'peakLimiter':{'ceilingAmplitude':.85,'purpose':'Fixed peak protection only; no phrase crescendo','latencyCompensated':True},'dryFile':str(drypath.relative_to(root)),'plot':candidate['plot'],'description':candidate['description']}
        reports.append(report)
    output={'clips':{k:r for k,(a,r) in prepared.items()},'candidates':reports};(root/spec['report']).write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n');return output


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('spec',type=Path);p.add_argument('--root',type=Path,default=Path('.'));args=p.parse_args();result=compose(json.loads(args.spec.read_text()),args.root)
    print(json.dumps({r['id']:{'seconds':r['seconds'],'LUFS':r['integratedLUFS'],'TP':r['truePeakDBTP']} for r in result['candidates'].copy()},indent=2))
