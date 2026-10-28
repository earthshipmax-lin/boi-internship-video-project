from pathlib import Path
import time
V=Path(__file__).resolve().parents[1];Q=V/'qa/v20'
while not (Q/'FINAL_QA.md').exists():time.sleep(3)
k=Path('/Users/linwenbin/Desktop/codex工作流/ex-wife/projects/boi-logo-reveal/STATUS.md');s=k.read_text();s=s.replace('updated: 2026-10-27','updated: 2026-10-28',1);s=s.replace('source: 用户要求清理全部已备份试片并检查磁盘；远端十卷再核验、缓存清理和成片校验','source: 用户采用Prompt20、选择保留音量与接点A并要求三语重做；本地V20验证',1)
block='''2026-10-28 最新：用户采用Prompt20删除所有人物段，并明确选择音乐接点A，三语均重做。普通话V20为73.233秒/2197帧、粤语76.267秒/2288帧、英文72.067秒/2162帧；位于工作区video/out/BOI-HK_史詩形象片_v20_{普通話,粵語,英文}_無人物版.mp4，各有20秒接点预览。根目录BOI-v20-三语无人物版_20261028.zip仅三片/说明/校验表，ZIP CRC及内部视频SHA通过。旧三语与压缩包保留。

从已归档03/04卷下载并校验整卷SHA，恢复14条所需音轨逐文件SHA一致，传输卷已移除。新制作遵循原先清理后的恢复流程，不代表其他归档卷全量恢复已验证。新入口src/index-v20.tsx，三份timeline-v20；人物镜/六句旁白字幕删除，信任句后静止0.6秒、内容上移淡出、空米白、树干/内外叶片生长再标题入场。三语独立时间轴保留语速；粤语比英文长属原发声长度。

用户明确选择原音量/PCM优先覆盖稿-16LUFS；成片约CN -14.05 / YUE -13.93 / EN -13.74 LUFS，TP均≤-1.2dBTP。A为较短等功率音乐桥接，非严格同拍小节认证；告知约90BPM但同拍无法可靠认证后用户试听选A。B较长淡化只是备选。独立旁白与删段前母带PCM一致，桥接后master对应样本相同；普通话V19获选片尾不变，AAC重编码不冒称逐样本一样。

三部主片及预览完整解码；6647帧OCR/人脸扫描与规范化人名匹配零检出（概率检测非绝对保证），24cue各无重叠/正文空窗>2.5秒；18抽样布局无越界、12非改动原生PNG零差、173保护文件SHA不变，typecheck通过。证据唯一位置工作区video/qa/v20/FINAL_QA.md、IMPLEMENTATION.md及各JSON。新整片待用户观看，A选定不扩大为整片批准。

本轮Prompt20明确不上傳、不发布，覆盖默认阶段自动推送：仅本地保存/本地提交，公开归档未更新，不能用旧远端状态冒称V20已备份。

## 前阶段：清理与归档

'''
s=s.replace('# 当前进度\n\n','# 当前进度\n\n'+block,1);k.write_text(s)
