from pathlib import Path
import json,shutil
V=Path(__file__).resolve().parents[1];Q=V/'qa/v16';r=json.loads((Q/'verification.json').read_text());assert r['full']['completeDecode'];K=Path('/Users/linwenbin/Desktop/codex工作流/ex-wife');files=['projects/boi-logo-reveal/STATUS.md','projects/boi-logo-reveal/DECISIONS.md','projects/INDEX.md'];B=Q/'knowledge-before'
for rel in files:
 p=K/rel;d=B/rel;d.parent.mkdir(parents=True,exist_ok=True)
 if not d.exists():shutil.copy2(p,d)
p=K/files[0];s=p.read_text().replace('source: 用户最新转场圆心、水印、人物和混音修订；V15三语与普通话片尾重录技术核对','source: 用户明确否定V15普通话片尾；V16同男声情绪、拖音与递进修订及技术核对',1)
new='''

2026-10-27 当前普通话改为V16“递进拖音版”，用户明确否定V15普通话尾段的情感效果；本次仅修改普通话片尾，粤语／英文继续V15，画面布局和此前人物／转场修正沿用。V16技术完成，情绪与自然度仍待用户试听，不能称已满意。

文件video/out/BOI-HK_史詩形象片_v16_普通話_遞進拖音版.mp4，98.733333秒／2962帧，片尾预览BOI-HK_v16_普通話片尾_遞進拖音預覽.mp4；续做入口video/qa/v16/FINAL_QA.md、IMPLEMENTATION.md及verification.json，src/index-v16.tsx、timeline-v16-cn.json、BOI-HK-Epic-v16-CN。没有V16粤／英新片。

声音同已批准BOI-HK-v13-R06-Clone-r01。网页Emotion不是克隆不支持，而是必须先选台词才启用；本次真实四段Happy，speech2.8-hd／speed0.88／pitch+1。两条生成各55点，共110点，最后观测6549点；r01字音有疑点未选，r02原WAV6.785417秒保留。保留图原发音、山／泰／际韵尾保音高WSOLA细延0.434938秒，选用干声7.220354秒；独立ASR全文逐字对应，并核对选用文件SHA。三句力度轻递增，最终新母带局部限峰，字幕跟随实际波形。听感仍由用户判断。

89.833333秒之前V15普通话母带PCM逐采样完全相同；原A音乐／轻BGM／duck保留。视频前2510帧（83.666667秒）H264流保留，从既有I帧接入新452帧尾段，逐帧解码前段framemd5与V15全部相同。最终完整解码／有声音轨／母带相关>0.999／无削波、30句活动字幕覆盖及12抽样边界核对通过；旧580保护项保持。早期内部候选和旧下载误取隔离在qa/v16，不是当前声源。

工程影片本地保存，知识库Git与远端同步另报。下一步用户试听V16尾段；无待登录、额度或配音阻塞。不上载／发布，不派发Claude。

## 前版：V15（以下为历史，普通话片尾以V16为准）
'''
s=s.replace('# 当前进度\n','# 当前进度\n'+new,1);p.write_text(s)
p=K/files[1];s=p.read_text()+'''

## 2026-10-27 普通话V16情绪递进与拖音

用户明确否定V15普通话片尾，覆盖其待听感状态，但未否定粤／英或V15画面。只出新普通话V16，当前三语映射为Yue/EN V15、CN V16，不制造不存在的V16三语片。

先选文字才可用网页Emotion，不能把未选中时disabled判断为模型或克隆不支持。真实Happy标记与标点／停顿分开记录，选用r02；字音疑点的r01只备份。局部拖音优先保留辅音和字调，图延展后辨识不佳即保留自然发音，只细修山／泰／际。最终独立ASR字词一致及源hash能证明诊断对象，不能证明用户情绪满意。

只重新制作末段混音，原89.833333秒前母带PCM保持；前2510画面帧由V15既有I帧边界复制后逐帧验证，末段为字幕同步而重渲。V15静帧composition muted覆盖问题已通过单独解析有声full props规避；完整音轨检查必须在交付前执行。事实与技术证据只维护video/qa/v16。
''';p.write_text(s)
p=K/files[2];s=p.read_text().replace('香港V15三语细节／混音精修完成，中心扩散、人物贴底／比例及普通话片尾重录，待观看；V14及美国V5保留','香港普通话V16情绪递进／拖音片尾已交付待听感；粤／英继续V15，旧版及美国V5保留');p.write_text(s)
print('V16 project knowledge saved in three scoped files.')
