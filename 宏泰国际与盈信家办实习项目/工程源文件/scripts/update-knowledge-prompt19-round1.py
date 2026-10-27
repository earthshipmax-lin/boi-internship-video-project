from pathlib import Path
import json,shutil
V=Path(__file__).resolve().parents[1];Q=V/'qa/v19';r=json.loads((Q/'audition-verification.json').read_text());assert all(t['ASRAcceptedExactOrAllowedHomophone'] for t in r['takes'].values());K=Path('/Users/linwenbin/Desktop/codex工作流/ex-wife');files=['projects/boi-logo-reveal/STATUS.md','projects/boi-logo-reveal/DECISIONS.md','projects/INDEX.md'];B=Q/'knowledge-before'
for rel in files:
 p=K/rel;d=B/rel;d.parent.mkdir(parents=True,exist_ok=True)
 if not d.exists():shutil.copy2(p,d)
p=K/files[0];s=p.read_text().replace('source: 用户明确否定V15普通话片尾；V16同男声情绪、拖音与递进修订及技术核对','source: 用户明确否定V16并采用Prompt19；第一句A/B/C试听、字音与静态增益验证；等待用户方向选择',1)
entry='''

2026-10-27 当前：用户明确否定V16普通话片尾，并采用CODEX_PROMPT_19_普通話片尾雄渾重錄.md。本轮只交第一句“大展宏图”A/B/C三条方向样音，等待用户选定方向；依稿第56行及69–71行，不跳到后两句、完整候选或接片。尚无V19影片。粤／英仍V15，V16文件仅作已否定历史保留。

唯一续做入口工作区video/qa/v19/ROUND1_README.md、plan.json、audition-verification.json。试听video/qa/v19/auditions/line1-A.wav、line1-B.wav、line1-C.wav；原始WAV在sources/，参数截图在proofs/。均原已批准BOI-HK-v13-R06-Clone-r01／speech2.8-hd／Chinese(Mandarin)／volume1。A speed0.82、pitch−1、无情绪，选take02，句末逗号；B0.85／0／无情绪；C0.80／−1／Neutral。网页无Calm，采用稿第3节允许的neutral并明确标注，不冒称用了calm。

三条只做格式转换及静态增益归一到约−16LUFS，TP≤−1dBTP；无Happy、正音高、EQ／混响、后期移调／WSOLA／time-stretch或渐强。字音独立ASR：A/B宏→红是稿允许同音替字，C逐字一致；选用均无图→土。A首次字音疑点，已隔离rejected/line1-A-take01，补录按同A参数自然重生。4take实际44点，选用33＋废稿11，余额6549→6505为历史观测；原估21点按页面计费修正三条基础33／九条93，后续六条约60点，重录另计。595旧保护项SHA保持，格式转换后恒定增益PCM拟合误差<2.5e−7、采样数和真实时长保持。ASR和响度不是语气合格证明。

下一步先用户听A/B/C选方向；然后第二／三句各三变体，拼两条完整片尾候选并附波形／停顿图，用户再选后才接V19电影。后续按“起—承—定”和低、慢、停、收，不恢复V16 Happy／升调／人工拉伸路线；同克隆既有授权不需重复确认。总长若超片尾窗口依稿回报后处理。

按用户本次新增阶段同步规则，video子项目已建立本地Git main，仅提交3个可安全同步的源文件（.gitignore、SOURCE_SYNC.md、通用voice-audition-tools.py），根提交cc8a2b8。客户提示词、音源／样音／影片、账号与QA原始记录仍本地，显式白名单防止批量历史上传。GitHub CLI未登录，已启动设备授权交由用户完成；未配置新远端／未建GitHub仓库／未推送。实际身份须登录后gh api user核验earthshipmax-lin，再按现有分支／远端和Private新仓规则继续。知识记录本地提交及远端状态另报，不声称同步成功。

## 前版：V16（用户已明确否定片尾，以下为历史）
'''
s=s.replace('# 当前进度\n','# 当前进度\n'+entry,1);p.write_text(s)
p=K/files[1];s=p.read_text()+'''

## 2026-10-27 Prompt19第一句试听关口

用户明确否定V16效果，采用Prompt19指定的雄浑“起—承—定”路线；不再使用Happy／正音高／后期元音拉伸／音量递增。用户这次对完整读法的否定不撤回此前克隆授权，但旧克隆获准也不等于新演绎已通过。

第56行明确先只录第一句3变体，方向获选后才录其余两句；第69–71行进一步要求两条完整片尾再次选后才接片。不可把“照着完成”解释为跳过这两次用户听感选择。C菜单只有Neutral无Calm，采用第3节明确允许的neutral并如实标注。A初次图／土疑点在原参数下用目标逗号补录，废稿隔离，扣点如实计入。

试听只做静态增益，原始WAV保留；PCM拟合和同样本数验证不能被表述为用户语气满意。后续胸腔EQ／大堂极轻混响依稿用于完整候选，不能通过后期拉长伪造气息。当前只交3条小样，无V19影片。

新阶段同步授权下，本阶段只将通用验证工具和同步边界提交到video新本地Git；原始客户资料和媒体默认不上传。GitHub身份未验证时不创建远端或推送，设备登录由用户完成；其他ex-wife工作区改动不夹带。
''';p.write_text(s)
p=K/files[2];s=p.read_text().replace('香港普通话V16情绪递进／拖音片尾已交付待听感；粤／英继续V15，旧版及美国V5保留','香港V16片尾被否定；Prompt19第一句A/B/C试听已交付待选，未接片；粤／英V15保留，GitHub登录待用户');p.write_text(s)
print('Prompt19 round1 project records saved.')
