from pathlib import Path
import json
V=Path(__file__).resolve().parents[1];Q=V/'qa/v13/redesign';K=Path('/Users/linwenbin/Desktop/codex工作流/ex-wife')
x=json.loads((Q/'verification.json').read_text());assert len(x['results'])==3 and not x['layoutFailures']
p=K/'projects/boi-logo-reveal/STATUS.md';s=p.read_text();head=s[:s.index('# 当前进度')];tail=s[s.index('## 并行保留：美国V5'):]
head=head.replace('source: 用户批准新账号上传原声复刻和条款；复刻保存与对照试听；字幕接口验证','source: 用户批准复刻与延长静止停留；最新蓝段缩短和Prompt15；三语成片解码与几何声轨验证')
body='''# 当前进度

2026-10-26 香港Prompt14未完成项已补齐，并按用户最新“蓝背景语句间隔略缩短”及CODEX_PROMPT_15_五鏡重設計.md输出三语重设计片。当前待用户观看，不是公司批准／对外发布。

当前文件均在工作区video/out/：BOI-HK_史詩形象片_v13_粵語_重設計版.mp4、BOI-HK_史詩形象片_v13_英文_重設計版.mp4、BOI-HK_史詩形象片_v13_簡中_重設計版.mp4。每片3426帧／114.20秒／1080p30；上一份Prompt14加长版3496帧／116.533333秒三片独立保存。唯一续做入口video/qa/v13/redesign/FINAL_QA.md、IMPLEMENTATION.md、verification.json及video/README.md。入口src/index-v13-redesign.tsx，复用BOI-HK-Epic-v13*三个ID；timeline-v13-redesign.json不可混用旧timeline。

用户批准复刻样音继续，也明确允许按完整配音统一延长镜头停留；不再等登录／额度／样音。63条新账户录音已保存（含2条数字替换，61条选用），加原5条共66条新配音。生产1777点加复刻58点，最后观测8165点；非当前实时余额。原账户153点独立历史。英文1.5billion／普通话100亿以r02入片；Whisper小模型误识别经small复核，不把ASR称为人工完整听审。

用户最新时长要求覆盖Prompt15时间不动条款：蓝段10处三语共同静音／极低电平间隔合计去70帧=2.333333秒。保留人声样本实测逐采样零差，无变速裁词；字幕及地图门控同一映射，米白段之后相对节奏保持。A曲60ms接缝再duck及母带处理，B/C只备份不载入。人物继续淡彩，无黑白，暖灰留白和1.6倍上限保留。

五镜：25标志米白alpha13/12双轨24px/s，银行下轨初始相位−850px避免边缘不可读；两幅完整对联+四奖杯一列（Whale/2022/2023/2024），删四证书画面；单一SVG Q、真实经纬度、44倍港深镜；平台96/40/36/20px放大避让；根深中文128px、树560px、英文700px限宽84px。三语平台文字最小间隔24/29/24px，奖项27px间隔／共同底边零差，主地图标签与航线包围盒不交，海岸三点误差<.004px，港深距离66.47px；根深中心差<1px。

具体规格冲突在IMPLEMENTATION如实记录：800ms地图按专门条款优先；根深固定128px和560px时墨迹面积比中文约1:2.06/2.11，英文约1:3.96，不达约1:1.2，未冒称；垂直中心优先于无法同时满足的底边对齐。20px下限指平台正文，水印／地图辅文有专门例外。照片与公司信息来源边界沿用原核对，不扩成对外批准。

三片完整解码通过，168张原生抽样记录0文字溢出／画布越界，三语保留声采样零差，476旧保护文件及3份Prompt14成片hash不变。20组五镜前后对照、实际编码音频核对、字幕SRT保存。银行相位最后单独重渲494–779帧并合片，音频copy、视频CRF18重编；不声称与旧片像素恒等。原版／检查版分开归档。美国V5完全独立保留。本次电影／源码仅本地保存；知识Git提交及远端同步另报。

下一步是用户观看这三份新版并反馈；没有未完成配音或网络阻塞，不重复追问已给的批准。不上载、不发布，也未派发Claude。

'''
p.write_text(head+body+tail)
p=K/'projects/boi-logo-reveal/DECISIONS.md';s=p.read_text();marker='# 范围与实现决定\n';new='''

## 2026-10-26 香港Prompt14补齐与Prompt15

- 用户批准复刻男声批量继续；共享配音长短差以静止停留延长，不加速、截尾。已完成三语长片。
- 最新直接要求蓝段句间略缩短优先于Prompt15冻结时轴，10个共同低电平区间去70帧；米白之后只整体平移。保留声样本零差，主观听感仍待用户。
- 五镜改版与银行轨道相位另存，不覆盖原三语加长片和美国V5。当前候选114.20秒；来源与具体几何取舍见工作区video/qa/v13/redesign/IMPLEMENTATION.md。
- 数值核对与视觉目标分开：平台间距／地图定位／奖项遮挡／中心对齐经测量通过；根深墨迹面积比例未达1:1.2，明确记录，不宣称全部条款无差异。
- 技术完整交付不等于用户／公司已批准；剩余动作是观看反馈，已解决网络及声音审批不再作为阻塞。
'''
p.write_text(s.replace(marker,marker+new,1))
p=K/'projects/INDEX.md';s=p.read_text();rows=s.splitlines();rows=[('| boi-logo-reveal | [定义](boi-logo-reveal/PROJECT.md) / [状态](boi-logo-reveal/STATUS.md) / [决定](boi-logo-reveal/DECISIONS.md) | 香港Prompt14配音补齐；Prompt15五镜三语114.20秒版已完成，蓝段去2.33秒，待观看；美国V5独立保留 |' if row.startswith('| boi-logo-reveal |') else row) for row in rows];p.write_text('\n'.join(rows)+'\n')
print('Updated only STATUS, DECISIONS, projects INDEX.')
