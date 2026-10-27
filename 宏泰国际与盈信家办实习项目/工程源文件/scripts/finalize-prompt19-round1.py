from pathlib import Path
import json,hashlib,shutil,subprocess
import numpy as np
V=Path(__file__).resolve().parents[1];R=V.parent;Q=V/'qa/v19';r=json.loads((Q/'audition-verification.json').read_text());assert all(t['ASRAcceptedExactOrAllowedHomophone'] for t in r['takes'].values())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pcm(p):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-ar','48000','-ac','2','-f','f32le','-']),dtype='<f4').astype(np.float64)
for name,t in r['takes'].items():
 src=V/t['source'];out=V/t['file'];assert sha(src)==t['sourceSHA256'] and sha(out)==t['sha256'];assert abs(t['seconds']-t['sourceSeconds'])<.00006
 a=pcm(src);b=pcm(out);assert len(a)==len(b);coef=float(np.dot(a,b)/np.dot(a,a));error=float(np.max(np.abs(b-a*coef)));assert error<2e-6,(name,error);t['staticGainPCMFit']={'gain':coef,'maxAbsoluteError':error,'sameDecodedSampleCount':len(a),'verifiedNoPostRetime':True}
protected=json.loads((Q/'protected-baseline.json').read_text());changed=[p for p,h in protected.items() if not (V/p).is_file() or sha(V/p)!=h];assert not changed,changed
r.update(protectedFilesUnchanged=len(protected),phase='round1_delivered_pending_user_choice',videoProduced=False,nextAction='After user selects direction, generate lines2/3 three variants each; assemble two complete endings for a second user selection; only then integrate V19 film.');(Q/'audition-verification.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
s='# Prompt19 第一轮：第一句三条试听\n\n2026-10-27。V16普通话片尾被用户明确否定；本次严格先交第一句方向样音，尚未生成后两句或V19视频。全部沿用已批准克隆，模型speech-2.8-hd，volume1，强制Chinese(Mandarin)。\n\n'
for n,t in r['takes'].items():s+=f"- {n}：[WAV试听](auditions/line1-{n}.wav)，{t['seconds']:.6f}秒；speed {t['speed']}／pitch {t['pitch']}／emotion {t['emotion'] or '无'}；{t['integratedLUFS']:.2f}LUFS／{t['truePeakDBTP']:.2f}dBTP；独立ASR：{t['ASR']}。\n"
s+='''
A选用take02，输入“大展——宏圖，”（按目标第一句的逗号收束）；首次take01识别图为土，已隔离rejected/line1-A-take01。B/C输入“大展——宏圖。”。ASR宏→红为提示词明确允许的同音替字，选用三条均无图→土。ASR不是用户语气验收。

C的网页菜单只有Neutral，没有Calm。采用Prompt19第3节允许的neutral，明确标为Neutral，不声称应用了calm。截图proofs/line1-C.png和生成结果标题{neutral}确认；A/B结果标题不带情绪标记。speed及pitch均由生成时设置；后期不调音高。

原始WAV分别在sources/，可试听副本只经立体声格式转换、静态增益响度匹配和48k立体声24bit导出。没有EQ／混响／动态渐强／WSOLA／time-stretch。逐PCM验证格式转换后只有恒定增益，误差<2e-6、采样数相同，原时长保留。胸腔EQ／极轻大堂混响依稿留到完整候选拼接阶段，不在第一句方向样音掩盖原声。

初始按字符数估21点／九条63点，网站计费A实际11点后已修正：基础三条33点／九条93点。A一次必要补录另11，第一轮实际44点，余额6549→6505；全部历史观测，非实时余额承诺。后两句各3条按示例估60点，合计生产含本次废稿约104点，重录另计。文本编辑残留在点击Generate前已清除，没有误生成旧Happy长稿扣费。

所有旧保护文件保持，具体数量见audition-verification.json。用户选择A/B/C方向后才继续六条后续单句，之后两条完整片尾候选再次交用户选，再接片。Prompt19第56行和第69–71行是明确分阶段要求，不是新增上传或克隆授权问题。

当前尚无V19成片，V16原文件保留为已否定的历史；粤语／英文仍V15。工程根非Git；知识记录Git与远端结果分别见DELIVERY_STATUS.md。
''';(Q/'ROUND1_README.md').write_text(s)
b=Q/'before-docs';b.mkdir(exist_ok=True)
for rel in ['README.md','../CLAUDE_HANDOFF.md','qa/v11/CURRENT_SELECTION.json']:
 p=V/rel;d=b/rel.replace('../','root/');d.parent.mkdir(parents=True,exist_ok=True)
 if not d.exists():shutil.copy2(p,d)
entry='''> **当前：Prompt19普通话片尾重录，第一轮三条方向样音已交付，等待用户选A/B/C（2026-10-27）。** 用户明确否定V16效果；按CODEX_PROMPT_19_普通話片尾雄渾重錄.md，使用原克隆、低速／低或原音高，无Happy、无后期拉伸、无递增音量。只生成第一句；未生成V19影片，未替换V16，粤／英继续V15。
>
> 续做只读qa/v19/ROUND1_README.md、plan.json、audition-verification.json及用户新选择。A0.82/−1/无情绪（take02逗号），B0.85/0/无情绪，C0.80/−1/Neutral（网页没有calm，依稿允许的neutral）。三条统一−16LUFS；本轮44点含A废稿11点，最后观测6505。用户选方向后生成第二／三句各三变体，再交两条完整片尾候选，用户再选后才接V19影片。

'''
links='[A试听](qa/v19/auditions/line1-A.wav) · [B试听](qa/v19/auditions/line1-B.wav) · [C试听](qa/v19/auditions/line1-C.wav) · [第一轮记录](qa/v19/ROUND1_README.md)。\n\n'
p=V/'README.md';old=p.read_text();p.write_text(entry+links+old[old.index('# 美国60秒'):])
p=R/'CLAUDE_HANDOFF.md';old=p.read_text();p.write_text(entry+'V16用户已明确拒绝，不能标为待认可或继续沿用其Happy/正音高/WSOLA路线；V19还没有成片。不要跳过Prompt19两次用户试听选择，不能把过去对克隆声线的批准当作本轮新读法已通过。\n\n'+old[old.index('> **最新入口：Prompt18美国'):])
p=V/'qa/v11/CURRENT_SELECTION.json';x=json.loads(p.read_text());x.update(updated='2026-10-27',phase='hk_prompt19_round1_delivered_pending_user_direction',next_gate='User selects first-line A/B/C; only then generate line2/3 variants, then user selects two full endings before V19 film.',voice_status='V16 Mandarin ending explicitly rejected. Prompt19 first-line A/B/C samples only; no V19 film yet. Existing clone authorization retained.');x['video_candidate']['locales']['cn']['status']='rejected_by_user_prompt19_rework_pending';x['prompt19']={'status':'round1_user_choice_pending','qa':'video/qa/v19/ROUND1_README.md','auditions':{n:'video/'+t['file'] for n,t in r['takes'].items()},'creditsUsed':44,'protectedUnchanged':len(protected),'videoProduced':False};p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n');print('Prompt19 round1 finalized:',len(protected),'protected files unchanged.')
