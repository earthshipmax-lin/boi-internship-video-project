from pathlib import Path
import json,hashlib,shutil
V=Path(__file__).resolve().parents[1];R=V.parent;Q=V/'qa/v19';S=Q/'round2';r=json.loads((S/'candidate-verification.json').read_text());assert all(x['ASRMatchesWithAllowedHongHomophone'] for x in r['candidates'])
for x in r['candidates']:assert hashlib.sha256((V/x['file']).read_bytes()).hexdigest()==x['sha256']
s='# Prompt19 第二轮：完整三句候选\n\n2026-10-27。用户原话“A我觉得整体节奏不错”，因此固定第一句A原录，继续第二／三句各三变体。当前交付两条完整三句配音，等待用户选定后才接入影片；尚无V19成片。\n\n'
for x in r['candidates']:
 s+=f"## {x['id']}\n\n[完整WAV](../{Path(x['file']).name}) · [波形与停顿图](../{Path(x['plot']).name})\n\n{x['seconds']:.2f}秒，{x['integratedLUFS']:.2f}LUFS／{x['truePeakDBTP']:.2f}dBTP。句间干声停顿实测{x['measuredInterPhraseGapsSeconds']}秒；品牌内{x['measuredInternalBrandPauseSeconds']:.2f}秒；独立ASR：{x['independentASR']}。\n\n"
s+='''## 选择与限制

两条前两句均为A参数／无情绪标记；候选1品牌名采用A（0.82／−1），候选2品牌名采用B（0.85／0）。第一句就是用户选定的同一原声，仅做既定固定EQ、响度匹配和静音布局，发声节奏不变。其余B/C及补录均保留在round2/sources，不是当前候选。

重要未达项：“山”在多条自然生成中仍只有约0.37–0.42秒（包含直接收音衰减），短于稿内0.6–0.8秒目标；ASR对齐词区约0.24–0.28秒，两种量测不能混称。没有通过后期拉伸、复制音节或移调伪造长音。两条完整候选供用户听整体韵味；若仍需更长自然收音，继续原生重录，不能冒称所有表演指标通过。

## 生成与处理链

同已批准BOI-HK-v13-R06-Clone-r01／speech-2.8-hd／Chinese(Mandarin)／volume1。后两句基础各A/B/C：0.82/−1/无，0.85/0/无，0.80/−1/Neutral（网页无calm，依稿允许neutral）。品牌名生成文本含<#0.25#>，但实际留白比标签长；在原始静音区域剪接为合格间隔，未动字头／字尾。

六条基础81点，三条自然收音补录32点，第二轮共113点，6505→6392为本次历史观测；Prompt19两轮累计157点（第一轮44）。补录中一条沿用了Neutral且0.82，已按真实属性单独命名，没有伪称无情绪A；两条长音补录在完整识别中出现“问如”／字音疑点，未采用。

每段只裁起止静音并保留呼吸余量；HP80Hz、200Hz/Q0.8/+1.5dB；3–5kHz不提亮。三句静态响度匹配、无渐强，接点10ms处理在静音处。山／际尾端送入RT60约1.2s的密集扩散房间IR，湿度4%，无孤立清晰回声；其他字不送混响。整体再做单一增益及固定峰值保护（非语气渐强），TP≤−1。无WSOLA／atempo／time-stretch／后期pitch shift。候选为纯三句配音；原A配乐未改，留待选定后接片，当前没有加新音效。

601旧保护项SHA保持，含第一轮已选A与所有旧影片／声音。完整候选字音和干声停顿符合检查，三句响度接近，原始源与所有中间片分别保存。波形图按实际干声安静区标注；混响余韵不当作新发音。ASR不是语气／雄浑程度验收。

技术数据candidate-verification.json、composition-report.json；原始参数／扣点／截图generation-log.json、proofs/；原声sources/。已被排除的内部拼接在iteration-r*，不得选作正式候选。下一步用户选完整候选1／2或要求继续重录，再依Prompt19第71行接V19及15秒片尾预览，不覆写V16。\n'''
(S/'ROUND2_README.md').write_text(s)
B=S/'before-docs';B.mkdir(exist_ok=True)
for rel in ['README.md','../CLAUDE_HANDOFF.md','qa/v11/CURRENT_SELECTION.json']:
 p=V/rel;d=B/rel.replace('../','root/');d.parent.mkdir(parents=True,exist_ok=True)
 if not d.exists():shutil.copy2(p,d)
entry='''> **当前：Prompt19第二轮，两条完整三句配音已交付，等待用户选择后才接片（2026-10-27）。** 用户确认“A整体节奏不错”，固定第一句A；候选1前两句A＋品牌名A，候选2前两句A＋品牌名B原音高。两条约7.10／7.03秒，句间约0.6／0.9秒、品牌内约0.27／0.25秒；−16LUFS附近，TP≤−1，无后期拉伸／升调／渐强。
>
> 未达项：山的原生收音约0.37–0.42秒，未稳定达到稿内0.6–0.8秒；不得称全指标通过。用户听两条后选1／2或继续原生重录，尚无V19影片。V16尾音已被明确否定；粤／英保持V15。只读qa/v19/round2/ROUND2_README.md、candidate-verification.json与用户新选择。第二轮113点，两轮累计157，最后观测6392。

'''
links='[完整候选1](qa/v19/ending-candidate-1.wav) · [候选1波形](qa/v19/ending-candidate-1-waveform.png) · [完整候选2](qa/v19/ending-candidate-2.wav) · [候选2波形](qa/v19/ending-candidate-2-waveform.png)。\n\n'
p=V/'README.md';old=p.read_text();p.write_text(entry+links+old[old.index('# 美国60秒'):])
p=R/'CLAUDE_HANDOFF.md';old=p.read_text();p.write_text(entry+'当前GitHub身份已实际核验earthshipmax-lin，video工具白名单有Private远端boi-video-workflow；只同步审查过的工具文本，不含音频／客户原始资料。当前阶段本地提交与远端SHA验证结果以qa/v19/round2/DELIVERY_STATUS.md为准，不沿用旧未登录提示。\n\n'+old[old.index('> **最新入口：Prompt18美国'):])
p=V/'qa/v11/CURRENT_SELECTION.json';x=json.loads(p.read_text());x.update(updated='2026-10-27',phase='hk_prompt19_two_complete_endings_pending_user_choice',next_gate='User selects complete candidate1/2 or asks for more native recording; only then integrate V19 film. Natural shan length remains below target.',voice_status='First-line A rhythm accepted. Two complete pure-voice candidates with fixed EQ and subtle tail room, no retiming/positive pitch/crescendo.');x['prompt19'].update(status='round2_complete_candidate_choice_pending',userDirection='A rhythm accepted',round2QA='video/qa/v19/round2/ROUND2_README.md',candidates={a['id']:{'file':'video/'+a['file'],'sha256':a['sha256'],'seconds':a['seconds'],'plot':'video/'+a['plot']} for a in r['candidates']},round2Credits=113,totalPrompt19Credits=157,nativeShanTargetMet=False,videoProduced=False);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n');print('Round2 delivery documents saved.')
