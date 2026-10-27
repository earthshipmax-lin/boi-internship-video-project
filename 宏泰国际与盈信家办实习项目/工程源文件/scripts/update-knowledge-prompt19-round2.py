from pathlib import Path
import json,shutil
V=Path(__file__).resolve().parents[1];Q=V/'qa/v19/round2';r=json.loads((Q/'candidate-verification.json').read_text());sync=json.loads((Q/'source-sync.json').read_text());assert all(x['ASRMatchesWithAllowedHongHomophone'] for x in r['candidates']) and sync['verifiedEqual'];K=Path('/Users/linwenbin/Desktop/codex工作流/ex-wife');files=['projects/boi-logo-reveal/STATUS.md','projects/boi-logo-reveal/DECISIONS.md','projects/INDEX.md'];B=Q/'knowledge-before'
for rel in files:
 p=K/rel;d=B/rel;d.parent.mkdir(parents=True,exist_ok=True)
 if not d.exists():shutil.copy2(p,d)
p=K/files[0];s=p.read_text().replace('source: 用户明确否定V16并采用Prompt19；第一句A/B/C试听、字音与静态增益验证；等待用户方向选择','source: 用户确认第一句A整体节奏；Prompt19第二轮两条完整候选、字音／停顿／响度核对；山自然长音未达目标，待完整候选选择',1)
entry='''

2026-10-27 当前：用户原话“A我觉得整体节奏不错”，已确认第一句A的整体节奏方向；本轮按Prompt19录后两句各三版及自然收音补录，现交两条完整三句纯配音，等待用户选完整候选1／2或继续重录。尚无V19影片，不能把第一句节奏认可当完整片尾批准。粤／英V15、V16原文件保留。

当前试听video/qa/v19/ending-candidate-1.wav（7.10秒）、ending-candidate-2.wav（7.03秒）；各有同名-waveform.png附实测停顿。续做只读video/qa/v19/round2/ROUND2_README.md、candidate-verification.json、composition-report.json和用户新选择。两条前两句均沿用A参数及原生无情绪录音；候选1品牌名A（0.82／−1），候选2品牌名B（0.85／0）。第一句始终同一已选A原声，发声不变速。

完整ASR两条均为“大展宏图 稳如泰山 宏泰国际”；句间干声安静区实测0.60／0.90秒，品牌内0.27／0.25秒。整体约−16.08／−16.07LUFS、TP−1.39dBTP；三句静态响度匹配，无渐强。固定HP80Hz、200Hz+1.5dB、仅山／际尾端4%湿度约1.2s扩散房间感、固定限峰保护。只剪接静音，未作WSOLA／time-stretch或后期移调；601旧保护项SHA不变。

重要未达项：山的自然收音在多次原生补录中未稳定达到0.6–0.8秒，当前采用的直接收音约0.37秒；试过的补录约0.32–0.42秒。两条候选明确带此限制供用户听感判断，不称全表演指标通过。补录在完整识别中出现“问如”的版本已排除，当前全部用发音清楚的第二句A原录。第二轮六条基础81点＋三条补录32点＝113点，6505→6392为历史观测；Prompt19两轮累计157点，原声／失败内部拼接／备选分别在round2/内隔离。

下一步依Prompt19第70–71行，用户选完整候选后才接入V19和15秒片尾预览。若用户要求更长原生山音，继续生成，不可用人工拉伸补达标。若未来影片需延长，依稿先回报再处理；当前两条均在原片尾窗口内可容纳，未改任何旧片。

GitHub身份已核验earthshipmax-lin，Private工具仓earthshipmax-lin/boi-video-workflow main本阶段00c16f0已推送，远端SHA重新读取与本地一致；只含已审阅通用源工具和同步说明，不含音频／客户原始资料／报告／模型。音频及工程数据本地保存；本次知识库提交与远端结果另报，完整同步记录见video/qa/v19/round2/DELIVERY_STATUS.md。

## 前轮：Prompt19第一句试听（A节奏已确认，以下为历史）
'''
s=s.replace('# 当前进度\n','# 当前进度\n'+entry,1);p.write_text(s)
p=K/files[1];s=p.read_text()+'''

## 2026-10-27 Prompt19：A节奏确认与完整候选

用户只确认第一句A整体节奏；保留同一第一句原录并生成两条完整候选，尚未获整段选择，不接片。两条差异集中在品牌名A低音高／B原音高，其余前两句沿用A参考。对照和补录未入选部分独立保存，不污染当前候选。

原生山音多次重录仍未稳定达到稿目标，必须将0.37秒实际收音与0.6–0.8秒要求并列说明；不能拿静音／混响尾巴或ASR对齐区假作发音延长。只有静音区域可剪接，品牌内以处理后干声实测0.27／0.25秒验收，不把<#0.25#>标签当结果。单句响度在起止静音整理后重新静态匹配，不能用递增音量替代雄浑感。

完整候选ASR／停顿／响度通过并不代表表演目标全通过；当前山音限制未达、用户听感待选。第一句认可不跳过第二次完整候选闸门。用户新阶段同步授权下，仅通用工具源文档进入Private仓，客户源音／候选／波形／报告全部本地；远端SHA相等后才称源工具同步成功。
''';p.write_text(s)
p=K/files[2];s=p.read_text().replace('香港V16片尾被否定；Prompt19第一句A/B/C试听已交付待选，未接片；粤／英V15保留，GitHub登录待用户','香港Prompt19第一句A节奏获选，两条完整配音候选待选；山原生长音未达目标，未接片；工具Private仓已同步');p.write_text(s)
print('Round2 scoped knowledge saved.')
