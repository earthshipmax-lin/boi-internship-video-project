from pathlib import Path
import json,time,hashlib,zipfile
import numpy as np
from PIL import Image
V=Path(__file__).resolve().parents[1];Q=V/'qa/v21'
while not (Q/'deliverables.json').exists() or len(json.load(open(Q/'deliverables.json')))!=3:time.sleep(3)
d=json.load(open(Q/'deliverables.json'));base=json.load(open(Q/'protected.json'));bad=[p for p,h in base.items() if hashlib.sha256((V/p).read_bytes()).hexdigest()!=h];assert not bad
rows=[]
for p in (Q/'frames').glob('*-old.png'):
 a=np.array(Image.open(p));b=np.array(Image.open(p.with_name(p.name.replace('-old','-new'))));mask=np.any(a!=b,axis=2);outside=mask.copy();outside[150:710,1060:1760]=False;assert not outside.any(),p;rows.append({'old':p.name,'changedPixels':int(mask.sum()),'changedPixelsOutsideTree':int(outside.sum())})
(Q/'verification.json').write_text(json.dumps({'protectedCount':len(base),'protectedChanged':bad,'nativePictureSamples':rows,'typecheckPassed':True,'sharedComponent':'OfficialBrandV10','sharedClock':'1.2 + elapsed * 2.05','allThreeAudioPacketAndPCMIdenticalToV20':True},indent=2))
text='''# V21 三语大树生长统一

用户2026-10-28截图要求根深镜的大树动画与片尾Logo生长一致，适用普通话、粤语及英文。

根深镜直接嵌入既有OfficialBrandV10组件，使用ClosingV14完全相同的seconds=1.2+elapsed*2.05；底线中心展开、原四次缓动、树干上行clip、各叶片原delay/透明度/20%→100%缩放全部复用，取消V20的快速分圈纯淡入。通过外层等比变换及700×560裁切保留原大树位置大小，字标在裁切区外。标题、字幕、镜头切点、时间轴不动。用户新反馈覆盖Prompt20先前对树生长500/600ms的局部数值。

三语时长不变：CN2197帧/73.233333秒、YUE2288帧/76.266667秒、EN2162帧/72.066667秒。

只重渲根深镜所在250帧GOP范围，边界见patch-plan.json；前后视频流直接复制，受GOP跨度影响其中含部分原片尾画面重编码。原生PNG片尾抽样零差，非整个片尾码流相同。各片重渲区外逐帧解码MD5均与V20完全相同。

音频完整复制V20原AAC：三语包内容、PTS/DTS/时长和解码PCM全部一致，没有重混、重录或整体重新编码。三部主片及三部9秒预览完整解码通过；npm run typecheck通过。保护源码和V20成片SHA保持，原生新旧抽样的变化只在大树矩形内。

官方组件未修改；没有引入新文字、人像或素材。V20的6647帧OCR/人脸筛查是前阶段证据，本轮没有重跑全片OCR，不把前阶段扫描冒称V21新扫描。

输出与SHA见deliverables.json，检查见verification.json。旧V20和旧压缩包保留。新V21打包仅含三部成片、说明和校验清单，CRC/内部SHA核验。本地保存/本地Git提交，不上传发布。技术通过，用户视觉认可待观看。
'''
(Q/'FINAL_QA.md').write_text(text)
zipPath=V.parent/'BOI-v21-三语树生长统一版_20261028.zip';assert not zipPath.exists()
with zipfile.ZipFile(zipPath,'x',compression=zipfile.ZIP_STORED) as z:
 for r in d.values():z.write(V/r['file'],Path(r['file']).name)
 z.writestr('说明.txt','V21：三语根深镜大树统一使用片尾Logo生长组件及速度。时长与声音保持V20，尚待用户观看。\n');z.writestr('SHA256.json',json.dumps({Path(r['file']).name:r['sha256'] for r in d.values()},ensure_ascii=False,indent=2))
with zipfile.ZipFile(zipPath) as z:
 assert z.testzip() is None;hs=json.loads(z.read('SHA256.json'));assert all(hashlib.sha256(z.read(n)).hexdigest()==h for n,h in hs.items())
(Q/'package-verification.json').write_text(json.dumps({'file':zipPath.name,'sha256':hashlib.file_digest(zipPath.open('rb'),'sha256').hexdigest(),'CRCAndAllVideoSHAValid':True},ensure_ascii=False,indent=2))
head='''> **2026-10-28 V21 大树生长统一**：用户要求三语根深镜与片尾Logo生长相同；新镜直接复用OfficialBrandV10和片尾同一时间映射，三语原时长/音频保持。入口video/src/index-v21.tsx，输出video/out/BOI-HK_史詩形象片_v21_{普通話,粵語,英文}_統一樹生成長版.mp4，各有9秒预览；项目根有BOI-v21-三语树生长统一版_20261028.zip。检查见video/qa/v21/FINAL_QA.md；技术完成，待用户观看。仅本地保存/提交，无上传发布。\n\n'''
for p in [V/'README.md',V.parent/'CLAUDE_HANDOFF.md']:p.write_text(head+p.read_text())
p=V/'qa/v11/CURRENT_SELECTION.json';x=json.load(open(p));x['previous_video_candidate_before_v21']=x['video_candidate'];x['video_candidate']={'entry':'video/src/index-v21.tsx','locales':d,'qa':'video/qa/v21/FINAL_QA.md','status':'technical_complete_pending_visual_review'};x['phase']='hk_v21_same_roots_and_ending_growth';x['next_gate']='User watches V21 tree-growth revision';p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
k=Path('/Users/linwenbin/Desktop/codex工作流/ex-wife/projects/boi-logo-reveal/STATUS.md');s=k.read_text();s=s.replace('# 当前进度\n\n','# 当前进度\n\n2026-10-28 V21最新：用户要求三语根深镜的大树与片尾Logo同一生长动画。已直接复用OfficialBrandV10及ClosingV14相同的1.2+elapsed×2.05时钟，保留原位置/大小/标题/24条字幕和时间轴。新入口src/index-v21.tsx，三部out/BOI-HK_史詩形象片_v21_{普通話,粵語,英文}_統一樹生成長版.mp4，附9秒预览及根目录BOI-v21-三语树生长统一版_20261028.zip。三语时长同V20，AAC包及时间/解码PCM完全相同，250帧重渲区外全部逐帧MD5相同；原生PNG变化仅大树区域，片尾抽样零差，旧保护SHA保持，typecheck/完整解码/ZIP CRC及SHA通过。本轮未重跑全片OCR，前阶段V20扫描不冒称V21验证。证据唯一位置video/qa/v21/FINAL_QA.md、verification.json和deliverables.json。技术完成待用户观看；按本阶段不上傳/不发布，只本地保存/提交。\n\n## 前阶段：V20\n\n',1);k.write_text(s)
print('QA DOCS AND PACKAGE READY')
