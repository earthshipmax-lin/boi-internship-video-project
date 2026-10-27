from pathlib import Path
import json,hashlib,shutil
V=Path(__file__).resolve().parents[1];R=V.parent;Q=V/'qa/v14';verify=json.loads((Q/'verification.json').read_text());pre=json.loads((Q/'preflight.json').read_text())
for r in verify['results'].values():assert hashlib.sha256((V/r['file']).read_bytes()).hexdigest()==r['sha256']
assert json.loads((Q/'english-final-voice-check.json').read_text())['normalizedRatio']==1
b=Q/'before-delivery-docs'
for rel in ['README.md','../CLAUDE_HANDOFF.md','qa/v11/CURRENT_SELECTION.json','qa/v13/people/PREPARATION_STATUS.md']:
 p=V/rel;target=b/rel.replace('../','root/');target.parent.mkdir(parents=True,exist_ok=True)
 if not target.exists():shutil.copy2(p,target)
entry='''> **当前香港版本：v14节奏与同步精修版（2026-10-27）已完成。** 用户直接反馈优先：平台改为左侧盈信独立动效＋右侧三业务／五服务整齐排列；蓝底提亮并保留渐变层次；大树约2秒按底座→干→六圈叶片生长，片尾Logo生长／中心展开保留。
>
> 粤语102.566667秒／3077帧，英文98.933333秒／2968帧，普通话98.733333秒／2962帧。三语按各自声音安排节奏，不再等待最长版本。字幕按实际声音边界重校，修正14处粤语迟入；90句语音活动帧均在字幕窗口内，字幕不重叠。英文30句完整重录和界面审校，独立ASR在统一数字格式后与最终人声稿完全对应；不是用户听感批准。
>
> 当前入口src/index-v14.tsx；三份timeline-v14-{yue,en,cn}.json；三个BOI-HK-Epic-v14*。197张原生抽样记录0文字越界，平台文字最小间距24／31／24px；522旧保护项保持，v13及美国V5独立留存。公司信息／肖像的既有来源边界保持，当前待用户观看。

'''
links='''[粤语完整版](out/BOI-HK_史詩形象片_v14_粵語_節奏與同步精修版.mp4) · [英文完整版](out/BOI-HK_史詩形象片_v14_英文_節奏與同步精修版.mp4) · [普通话／简中完整版](out/BOI-HK_史詩形象片_v14_簡中_節奏與同步精修版.mp4) · [平台与生长重点预览](out/BOI-HK_v14_平台與樹形生長_重點預覽.mp4) · [技术核对](qa/v14/FINAL_QA.md) · [英文逐句审校](qa/v14/ENGLISH_REVIEW.md)。
'''
p=V/'README.md';s=p.read_text();p.write_text(entry+links+'\n\n'+s[s.index('# 美国60秒'):])
p=R/'CLAUDE_HANDOFF.md';s=p.read_text();p.write_text(entry+'当前只读video/qa/v14/FINAL_QA.md、IMPLEMENTATION.md、ENGLISH_REVIEW.md及verification.json。重现：node scripts/render-refined-v14.mjs（拒绝覆写）。本版三语时长不同是用户节奏反馈下按实际语音的适配；旧v13共用时轴只用于源画面映射，不能恢复为当前字幕。英文Singapore连线按实际单词起点39.698333秒，不按整句开头。\n\n'+s[s.index('> **最新入口：Prompt18美国'):])
p=V/'qa/v11/CURRENT_SELECTION.json';x=json.loads(p.read_text());x['prior_v13_redesign_candidate']=x['video_candidate'];x.update({'updated':'2026-10-27','phase':'hk_v14_refined_complete_pending_user_review','evidence':'user_requested_revision; technical_validation_complete; subjective_film_approval_pending','next_gate':'User watches V14 three-language refined films. No unresolved production blocker.','voice_status':'Yue/CN preserved at1x with quieter gaps trimmed. EN30-cue revised narration recorded with previously approved clone; normalized final ASR matches full script.','video_candidate':{'path':'video/'+verify['results']['yue']['file'],'composition':'BOI-HK-Epic-v14','entry':'video/src/index-v14.tsx','duration_seconds':verify['results']['yue']['seconds'],'status':'completed_internal_review_not_user_approved','qa':'video/qa/v14/verification.json','sha256':verify['results']['yue']['sha256'],'locales':{l:{'path':'video/'+r['file'],'seconds':r['seconds'],'frames':r['frames']} for l,r in verify['results'].items()},'preview':'video/out/BOI-HK_v14_平台與樹形生長_重點預覽.mp4'},'prompt14_preparation':{**x['prompt14_preparation'],'status':'complete_historical_source_for_v14'},'v14':{'scope':'platform spacing and entrance; pacing; speech/subtitles; lighter blue; restored tree growth; plain elegant US English','englishReview':'video/qa/v14/ENGLISH_REVIEW.md','protectedUnchanged':verify['protectedFilesUnchanged']}})
p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
(V/'qa/v13/people/PREPARATION_STATUS.md').write_text('# 当前制作已完成：v14精修版\n\n2026-10-27。Prompt14配音任务及v13已完成，用户最新反馈形成v14；不再存在复刻试听、网络、额度或剩余配音阻塞。当前入口video/qa/v14/FINAL_QA.md、README和CURRENT_SELECTION。粤102.566667秒／英98.933333秒／普98.733333秒，实际发声字幕同步、平台及树形动效修复，英文30句新录。原暖灰、淡彩、不黑白、1.6倍上限仍保留。下一步用户看当前三个新文件；旧v13是历史参考。\n')
s='''# v14最终技术核对

2026-10-27。根据用户当前截图与直接反馈完成，当前为待观看内部版本。

## 三语影片

'''
for l,r in verify['results'].items():s+=f"- {l}：[视频](../../{r['file']})；{r['seconds']:.6f}秒／{r['frames']}帧；{r['bytes']}字节；SHA256 {r['sha256']}。\n"
s+='''
三片1080p30／H264／AAC48k立体声；完整解码通过。容器AAC尾垫与视频时长分开记录。重点预览已完整解码，覆盖平台完整入场、大树和片尾Logo生长，带语音预留片头，避免预览切掉首字。

## 字幕与节奏

三语共90句；按实际声波和真实配音布局，逐帧检查−38dBFS以上语音活动均有字幕，字幕窗口无交叠。粤语旧表有14个入点迟于语音，已提前；细节caption-boundary-corrections.json。该指标证明起止覆盖，不是逐音素人工认证。粤／普只从已核对的句间低电平删除静音，保留声音不变速；英文新稿1倍速录制、拆句排布。源片相对映射与新的字幕时轴分开，避免字幕沿旧文件长度等待。

三语由旧114.20秒分别缩短11.633333／15.266667／15.466667秒。按各自语音安排时长，替代此前按最长语言统一等待的方式。音乐继续A，B/C备份不读，保留人声压低音乐。片尾品牌有停留供观看。

## 平台、颜色与生长

197张当前原生抽样记录0文字框溢出／画布越界；平台正文最小22px（服务节点更大），稳定文字框最小间距粤24／英31／简24px。左侧盈信中心遮罩展开、缩放及上移，标志和说明错开入场；右侧三列等基线，下方五个服务等距。evergreen-entry.jpg和platform-before-after.jpg为动效与版式证据。

蓝色为#124967／#1B6489／#205F83，两处柔光明暗与年轮提供层次。基础米白正文色对比5.63–8.36；不把此值扩成所有水印、半透明入场或图片内文字均达标。

大树底座0–.35秒、干.22–.87秒、六圈叶片约.62–1.98秒，通过新时轴实际经过时间驱动。三语九帧蓝色面积单调增加，最终133400蓝像素；官方树形的终态700×560原生PNG区域与v13参考逐像素零差。源路径／渐变保持，片尾Logo同样从底座生长、中文及英文从中间展开。原生PNG相同不代表H264逐像素相同。

## 英文核对

30句口播与字幕全部换成审校稿；完整记录见ENGLISH_REVIEW.md。独立Whisper small对原始和最终EN人声核对，在统一1.5／20,000／30等数字格式后全稿逐词对应。保留1997、HK$10B／HK$1.5B、20,000、正式人名和新加坡筹备状态；普通观众易懂用词取代every trust／guardian等直译。最终英文Singapore连线39.698333秒在念出该地名时启动，并让标签随接近出现以便阅读。此为语言／内容技术核对，没有声称美国受众实测或真人发音验收。

英文正式1429点，另26点为编辑器旧状态误生成测试，未入片；最后观测6710点。原声音、克隆批准和源WAV完整保留。

## 实际编码音频

'''
for l,r in verify['results'].items():s+=f"- {l}：{r['integratedLUFS']:.2f}LUFS／{r['truePeakDBTP']:.2f}dBTP；对母带相关{r['audioCorrelationToMaster']:.9f}。\n"
s+=f"\n无数字削波；{verify['protectedFilesUnchanged']}旧文件SHA不变，含旧v13成片、源画面、声音及美国V5。TypeScript通过。旧版不覆写，新版没有上传、发布或派发Claude。工程／媒体本地保存，知识库提交及远端状态另报。\n"
s+='\n证据：verification.json、preflight.json、animation-visual-check.json、english-final-voice-check.json、actual-storyboard.jpg、三语SRT。\n'
(Q/'FINAL_QA.md').write_text(s)
print('V14 delivery docs saved.')
