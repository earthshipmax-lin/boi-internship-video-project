from pathlib import Path
import json,shutil
V=Path(__file__).resolve().parents[1];Q=V/'qa/v15';K=Path('/Users/linwenbin/Desktop/codex工作流/ex-wife');r=json.loads((Q/'verification.json').read_text());assert len(r['results'])==3
b=Q/'knowledge-before';b.mkdir(exist_ok=True)
files=['projects/boi-logo-reveal/STATUS.md','projects/boi-logo-reveal/DECISIONS.md','projects/INDEX.md']
for rel in files:
 p=K/rel;dst=b/rel;dst.parent.mkdir(parents=True,exist_ok=True)
 if not dst.exists():shutil.copy2(p,dst)
p=K/files[0];s=p.read_text();s=s.replace('source: 用户最新六项修订；v14三语成片、字幕活动边界、英文审校及动效验证','source: 用户最新转场圆心、水印、人物和混音修订；V15三语与普通话片尾重录技术核对',1)
body='''

2026-10-27 当前香港候选为V15“细节与声音精修版”，按最新截图六项反馈完成三语；待用户观看，特别是普通话新片尾听感，不代表公司批准。唯一续做入口工作区video/qa/v15/FINAL_QA.md、IMPLEMENTATION.md、VOICE_PROVENANCE.md、verification.json，src/index-v15.tsx及timeline-v15-{yue,en,cn}.json，三个BOI-HK-Epic-v15*。

影片video/out/BOI-HK_史詩形象片_v15_粵語_細節與聲音精修版.mp4，英文／簡中同名。粤102.566667秒／英98.933333秒／普98.733333秒，保持V14三语各自自然时长；新重点预览BOI-HK_v15_中心轉場與人物及普通話片尾_重點預覽.mp4。旧V14和美国V5继续独立留存。

扩散圆心960,540，按当前转场实际窗口重新驱动完整从零进度，修复缩短停顿后跳过起步；全片左下审片／合并小字关闭，主要字幕保持。郑健丽按原图alpha底边锚定相框下边，抽样误差最大0.012px；胡忠瑶在相同300×400卡片内等比缩小25%，实际倍率约1.163；淡彩和1.6上限保留。人声源+1.5dB／A曲源−1.5dB、继续duck、母带目标−13.8LUFS／−1.3dBTP；非最终每一时刻恒定增益差。

普通话片尾同已批准BOI-HK-v13-R06-Clone-r01重录6.28725秒，生成语速0.94，明确三段停顿，完整源和尾音保留。MiniMax51点／6710→6659为本次历史观测，非实时余额；无新条款／登录阻塞。独立ASR对应“大展宏图，稳如泰山。宏泰，国际。”，最终两个字幕随波形更新；情绪／自然度需用户试听。粤／英全声与普片尾前原声仅增益、无变速，英文沿用V14美式审校稿。

三片1080p30、AAC48k立体声完整解码／母带相关>0.999、无数字削波；原生三语文字边界及90句语音活动字幕覆盖通过。保护旧文件及具体量测见verification。工程／媒体本地保存；知识库Git提交与远端结果单独报告，不上传／发布／派发Claude。下一步用户看三份V15，无未完成制作阻塞。

## 前版：V14（以下为历史，当前以V15为准）
'''
s=s.replace('# 当前进度\n','# 当前进度\n'+body,1);p.write_text(s)
p=K/files[1];s=p.read_text();s+='''

## 2026-10-27 香港V15截图六项精修

用户直接要求覆盖旧左下水印保留规则；仅当前V15关闭审片及合并小字，历史来源档案和旧片不删除。源年轮中心不应当作转场中心：画布圆心960,540，且新剪辑映射不能跳过扩散起步，按实际当前窗口重新计算完整进度而不延长整片。

人物同外框的均衡靠图像本身等比缩放与alpha底边定位；郑健丽贴底、胡忠瑶缩小25%，不拉伸／AI补身，弱彩和1.6上限继续。VO+1.5dB、BGM−1.5dB指母带前总线，经过duck与归一化后不冒称任意位置固定相同差值。

同已批准克隆重录普通话最后两句，不重复询问已批准声线；明确标点／停顿标签与实际静音分开记录。完整源尾音保留，字幕跟随实际波形；ASR字词正确不证明激昂感或真人感。旧V14、美国V5和声音完整保护，技术交付待用户听感。证据只维护在工作区video/qa/v15。
''';p.write_text(s)
p=K/files[2];s=p.read_text();s=s.replace('香港v14三语节奏／同步／平台与生长精修完成，英稿审校重录，待观看；v13及美国V5保留','香港V15三语细节／混音精修完成，中心扩散、人物贴底／比例及普通话片尾重录，待观看；V14及美国V5保留');p.write_text(s)
print('Knowledge project files saved (three scoped files only).')
