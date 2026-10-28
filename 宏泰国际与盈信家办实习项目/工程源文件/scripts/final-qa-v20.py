from pathlib import Path
import json,time,subprocess
V=Path(__file__).resolve().parents[1];Q=V/'qa/v20'
reports={}
for loc in ['cn','yue','en']:
 p=Q/f'{loc}-ocr-summary.json'
 while not p.exists():time.sleep(4)
 s=json.load(open(p));terms=s['terms']
 norm=lambda x:''.join(c for c in x.casefold() if c.isalnum())
 hits=[]
 for line in (Q/f'{loc}-ocr.jsonl').read_text().splitlines():
  r=json.loads(line);n=norm(''.join(r['text']));found=[x for x in terms if norm(x) in n]
  if found:hits.append({'frame':r['frame'],'terms':found,'text':r['text']})
 t=json.load(open(V/f'src/config/timeline-v20-{loc}.json'));assert s['frames']==t['durationInFrames'];reports[loc]={'frames':s['frames'],'allFramesProcessed':s['all_frames_processed'],'nameMatchesNormalized':hits,'faceMatches':s['faceMatches']}
(Q/'all-frame-screening.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2));print(json.dumps(reports,ensure_ascii=False,indent=2))
assert all(not s['nameMatchesNormalized'] and not s['faceMatches'] for s in reports.values()),'Review detection hits before marking complete'
text='''# V20 技术检查完成，整片待用户观看

2026-10-28：用户采用音乐接点A，明确要求三语都重做；保留原音量与PCM一致性的决定优先于稿中-16 LUFS。

| 版本 | 时长 | 帧数 | 成片LUFS | True peak |
|---|---:|---:|---:|---:|
| 普通话 | 73.233秒 | 2197 | -14.05 | -1.28dBTP |
| 粤语 | 76.267秒 | 2288 | -13.93 | -1.20dBTP |
| 英文 | 72.067秒 | 2162 | -13.74 | -1.24dBTP |

- 三语均1920×1080、30fps、H.264/AAC；三部主片与三部20秒预览完整解码通过。
- 共6647编码帧逐帧Apple Vision文字识别及人脸检测；另对OCR逐帧文本作去空白/标点、忽略大小写的人名匹配。未检出人名、人脸或“专业，由人而来”。扫描对象与交付片视频码流SHA一致。算法检测可能漏检，不能将零检出写成绝对保证。
- 每版24条字幕；无人物cue、无交叠、正文字幕间空窗均≤2.5秒。
- 三语母带删段前PCM逐样本相同；独立voice删段后只作位移且PCM相同；A桥接之外的后段master逐样本一致，普通话V19获选片尾保持。AAC重编码不声称PCM完全相同。
- 173个保护文件SHA未变；12个未修改位置原生PNG逐像素一致。不是全片逐帧像素比对。
- 18个转场/尾段关键帧排版检测无超画布；已查看淡出、空米白、树干展开、标题进场和英文完成帧。
- npm run typecheck通过。

音乐严格同拍/同调小节未能认证；按稿回报并提供A/B试听后，用户选择A。该选择与声音一致性优先为明确例外，不能写成原稿所有数值条件全达标。A为同接点较短等功率桥接，B为较长桥接；不是两个已认证同拍小节。

入口：src/index-v20.tsx。输出及SHA见deliverables.json；动作/节奏说明见IMPLEMENTATION.md，原生PCM核验见sample-parity.json，画面比对见picture-parity.json，逐帧扫描见all-frame-screening.json。

旧三语交付与压缩包保留。本轮本地保存/提交，不上传、不发布；新整片主观认可待用户观看。
'''
(Q/'FINAL_QA.md').write_text(text)
