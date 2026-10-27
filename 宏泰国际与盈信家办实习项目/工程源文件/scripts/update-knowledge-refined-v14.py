from pathlib import Path
import json,re
V=Path(__file__).resolve().parents[1];Q=V/'qa/v14';K=Path('/Users/linwenbin/Desktop/codex工作流/ex-wife');v=json.loads((Q/'verification.json').read_text());assert len(v['results'])==3
p=K/'projects/boi-logo-reveal/STATUS.md';s=p.read_text();s=s.replace('updated: 2026-10-26','updated: 2026-10-27',1);s=re.sub(r'^source:.*$', 'source: 用户最新六项修订；v14三语成片、字幕活动边界、英文审校及动效验证',s,count=1,flags=re.M)
marker='# 当前进度\n';new='''

2026-10-27 当前香港候选已更新为v14“节奏与同步精修版”，按用户最新截图处理盈信入场／右侧均衡、全片再提速、配音字幕同步、蓝底再提亮、补回树形生长，以及普通美国观众易懂的英文。三语已完整输出并技术核对，待用户看／听，不代表公司批准。

工作区video/out/：BOI-HK_史詩形象片_v14_粵語_節奏與同步精修版.mp4（102.566667秒／3077帧）、英文同名（98.933333秒／2968帧）、簡中同名（98.733333秒／2962帧）；重点预览BOI-HK_v14_平台與樹形生長_重點預覽.mp4。唯一当前入口video/qa/v14/FINAL_QA.md、IMPLEMENTATION.md、ENGLISH_REVIEW.md与verification.json，src/index-v14.tsx及三份timeline-v14-{yue,en,cn}.json；原BOI-HK-Epic-v14*独立入口，旧v13只作源画面映射。

平台改为左侧270px盈信标志遮罩展开＋轻缩放上移／文字错开，右侧三业务同基线／下方五服务等距。蓝色#124967→#1B6489→#205F83＋柔和明暗渐变／年轮。大树用官方原路径渐变，底座／干／六圈叶片约2秒生长，真实新时轴驱动；终态700×560原生树形区域与v13零像素差。片尾完整Logo从底座生长、字标中心展开。淡彩人物及1.6倍上限保持。

用户本次节奏与同步要求取代旧共同等待时轴：三语各按实际声音排布，较114.2秒分别缩短11.63／15.27／15.47秒。粤／普只去测得低电平句间、不变速人声；英文30句新稿同已获准复刻声线1倍速生成并拆句安排。字幕按声音边界，14处粤语旧表迟入已修正；90句−38dBFS以上语音活动均有字幕、无重叠。边界覆盖不等同人工逐音素认证。

英文口播与界面为自然美国英语，例every trust→the trust families place in us、结尾Think big. Stand strong.；保留1997、HK$10B／HK$1.5B、20,000、正式人名和新加坡筹备状态。独立Whisper small对原始及最终人声在数字格式统一后逐词一致；英语人名音质／观众听感仍待用户。英文Singapore位于句末，线路改在实际单词39.698333秒起跑，不能用句首触发。新声源public/vo/hk-v14/en/full-source.wav与VOICE_PROVENANCE独立保存；正式1429点，另26点编辑器旧状态误生成未入片，总1455，最后观测6710（非实时余额）。

三片1080p30／H264／AAC48k立体声完整解码、母带相关／无削波检查通过；197原生记录无文本越界，平台最小文字框间距24／31／24px，522旧保护文件SHA保持。24秒左右重点预览／动效序列／真实编码分镜／三语SRT已存。最终英文单词门控重渲时一次本机localhost无响应，降低并发重试成功；失败片隔离，不是最终候选。V13及美国V5留存，A音乐继续，B/C不加载；不上传、不发布、不派发Claude。

下一步用户观看这三份v14再反馈；没有未完成配音、登录或网络阻塞。工程／媒体本地保存，知识库Git和远端结果分别报告。

## 前版：香港v13重设计（以下是历史，当前以v14为准）
'''
s=s.replace(marker,marker+new,1);p.write_text(s)
p=K/'projects/boi-logo-reveal/DECISIONS.md';s=p.read_text().replace('updated: 2026-10-26','updated: 2026-10-27',1);marker='# 范围与实现决定\n';s=s.replace(marker,marker+'''

## 2026-10-27 v14直接反馈修订

- 用户新要求优先于旧平台环图和共同等长时轴：盈信有完整入场，右侧改整齐三列／五服务，三语按声音各自安排自然节奏。
- 字幕按实际发声起止，不按含留白文件长度；粤语14处迟入修复。音频活动覆盖是技术边界，不代替听感验收。
- 英文30句与画面文案重新审校／录制，保持已批准声线和来源事实。新加坡按实际单词触发，防止英文句尾地名提前连线。
- 树形保留官方终态，用约2秒明显生长；蓝底更亮而有渐变层次。旧v13／美国V5不动，新增媒体和证据独立保存。
- 当前只算技术交付完成，下一步用户看v14，不把英文语言核对／原生检查推成美国受众或公司批准。
''',1);p.write_text(s)
p=K/'projects/INDEX.md';s=p.read_text();s='\n'.join('| boi-logo-reveal | [定义](boi-logo-reveal/PROJECT.md) / [状态](boi-logo-reveal/STATUS.md) / [决定](boi-logo-reveal/DECISIONS.md) | 香港v14三语节奏／同步／平台与生长精修完成，英稿审校重录，待观看；v13及美国V5保留 |' if l.startswith('| boi-logo-reveal |') else l for l in s.splitlines())+'\n';p.write_text(s)
print('Updated only project STATUS, DECISIONS, INDEX.')
