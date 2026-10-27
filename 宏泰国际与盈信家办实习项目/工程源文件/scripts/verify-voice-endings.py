"""Verify and plot private local narration candidates from JSON manifests."""
from pathlib import Path
import argparse, hashlib, json, re, subprocess
import numpy as np
import torch, whisper
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties


def read(path):
    return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-ar','48000','-ac','2','-f','f32le','-']),dtype='<f4').reshape(-1,2)


def normalize(text):
    mapping=str.maketrans({'圖':'图','穩':'稳','國':'国','際':'际','紅':'宏','红':'宏','洪':'宏'})
    return re.sub(r'[^\u4e00-\u9fff]','',text.translate(mapping))


def quiet_runs(a):
    env=np.array([np.max(np.abs(a[i:i+480])) for i in range(0,len(a),480)])
    rows=[];start=None
    for i,v in enumerate(env):
        if v<=.01 and start is None:start=i
        if (v>.01 or i==len(env)-1) and start is not None:
            if i-start>=12:rows.append([start*.01,i*.01,(i-start)*.01])
            start=None
    return rows


def verify(spec,root,protected,model_name):
    report=json.loads((root/spec['report']).read_text());torch.set_num_threads(4)
    prior=root/spec['verification'];cached={r['sha256']:r['independentASR'] for r in json.loads(prior.read_text())['candidates']} if prior.exists() else {};model=None
    font=FontProperties(fname=str(root/spec['font']));results=[]
    for cand in report['candidates']:
        p=root/cand['file'];a=read(p);dry=read(root/cand['dryFile'])
        assert hashlib.sha256(p.read_bytes()).hexdigest()==cand['sha256']
        assert -16.5<=cand['integratedLUFS']<=-15.5 and cand['truePeakDBTP']<=-1
        assert 6.5<=cand['seconds']<=7.5
        transcript=cached.get(cand['sha256'])
        if transcript is None:
            if model is None:model=whisper.load_model(model_name,device='cpu',download_root=str(root/'.model-cache'))
            transcript=model.transcribe(str(p),language='zh',fp16=False,verbose=None)['text']
        text_ok=normalize(transcript)==normalize(spec['expectedASR'])
        runs=quiet_runs(dry);pos=cand['placements'];brand=pos[2]
        internal=[x for x in runs if x[0]>=brand['speechStartSeconds']+.25 and x[1]<brand['speechEndSeconds']-.25]
        assert internal,(cand['id'],'No internal brand pause')
        gap=max(internal,key=lambda x:x[2]);assert .20<=gap[2]<=.30,(cand['id'],gap)
        macro=[]
        for left,right,target in zip(pos,pos[1:],[.6,.9]):
            center=(left['speechEndSeconds']+right['speechStartSeconds'])/2
            run=min(runs,key=lambda x:abs((x[0]+x[1])/2-center));assert abs(run[2]-target)<=.10,(cand['id'],target,run);macro.append(run)
        for value,target in zip(cand['interPhraseGapsSeconds'],[.6,.9]):assert abs(value-target)<1/48000
        # Phrase loudness is evaluated on equal-EQ, static-matched dry clips.
        levels=[report['clips'][x['id']]['clipLUFS'] for x in pos];assert max(levels)-min(levels)<=1
        row={**cand,'independentASR':transcript,'ASRMatchesWithAllowedHongHomophone':text_ok,'measuredInterPhraseGapsSeconds':[x[2] for x in macro],'measuredInterPhrasePauseRanges':macro,'measuredInternalBrandPauseSeconds':gap[2],'internalPauseRangeSeconds':gap[:2],'dryClauseLUFS':levels,'nativeShanTargetMet':spec['sourceTailTargetMet'],'nativeShanLimitation':spec['nativeTailLimitation']};results.append(row)
        t=np.arange(len(a))/48000;fig,ax=plt.subplots(figsize=(13,3.6),dpi=150);fig.patch.set_facecolor('#f4eee2');ax.set_facecolor('#f4eee2');ax.plot(t[::24],a[::24,0],color='#145d83',lw=.5)
        for i,piece in enumerate(pos):
            ax.axvspan(piece['speechStartSeconds'],piece['speechEndSeconds'],alpha=.06,color='#145d83');ax.text((piece['speechStartSeconds']+piece['speechEndSeconds'])/2,.76,spec['phraseLabels'][i],fontproperties=font,ha='center',fontsize=10)
        for start,end,label in [(macro[0][0],macro[0][1],f'句间停顿 {macro[0][2]:.2f}s'),(macro[1][0],macro[1][1],f'句间停顿 {macro[1][2]:.2f}s'),(gap[0],gap[1],f'品牌内停顿 {gap[2]:.2f}s')]:
            ax.axvspan(start,end,color='#bd7448',alpha=.16);ax.annotate('',xy=(start,-.62),xytext=(end,-.62),arrowprops={'arrowstyle':'<->','color':'#9a562e'});ax.text((start+end)/2,-.84,label,fontproperties=font,ha='center',fontsize=8)
        ax.set_title(cand['id']+' | '+spec['candidateLabels'][cand['id']],fontproperties=font,fontsize=12);ax.set_xlim(0,cand['seconds']);ax.set_ylim(-1,1);ax.set_xlabel('Time / seconds');ax.set_ylabel('Amplitude');ax.grid(alpha=.15);fig.tight_layout();fig.savefig(root/cand['plot']);plt.close(fig)
        print(cand['id'],transcript,'brandGap',gap[2],flush=True)
    baseline=json.loads((root/protected).read_text());changes=[p for p,h in baseline.items() if not (root/p).is_file() or hashlib.sha256((root/p).read_bytes()).hexdigest()!=h];assert not changes,changes
    final={'status':'complete_candidates_pending_user_selection','candidates':results,'protectedFilesUnchanged':len(baseline),'noFilmProduced':True,'nativeShanTargetMet':spec['sourceTailTargetMet'],'limits':['Speech emotion and naturalness require user listening.','Natural shan duration still below target; no artificial lengthening performed.','Pause measurements use primary dry voice; quiet room decay is excluded from phonation.']};(root/spec['verification']).write_text(json.dumps(final,ensure_ascii=False,indent=2)+'\n');assert all(x['ASRMatchesWithAllowedHongHomophone'] for x in results),'A candidate requires word review';return final


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('spec',type=Path);p.add_argument('--root',type=Path,default=Path('.'));p.add_argument('--protected',type=Path,required=True);p.add_argument('--asr-model',default='small');args=p.parse_args();verify(json.loads(args.spec.read_text()),args.root,args.protected,args.asr_model)
