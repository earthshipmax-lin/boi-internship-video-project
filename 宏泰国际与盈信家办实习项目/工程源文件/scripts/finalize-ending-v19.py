from pathlib import Path
import json,shutil,hashlib
V=Path(__file__).resolve().parents[1];Q=V/'qa/v19/film';r=json.loads((Q/'verification.json').read_text());a=json.loads((Q/'audio-implementation.json').read_text());assert r['full']['completeDecode'] and r['preview']['completeDecode']
B=Q/'before-docs';B.mkdir(exist_ok=True)
for rel in ['README.md','../CLAUDE_HANDOFF.md','qa/v11/CURRENT_SELECTION.json']:
 p=V/rel;dst=B/rel.replace('../','root/');dst.parent.mkdir(parents=True,exist_ok=True)
 if not dst.exists():shutil.copy2(p,dst)
entry='''> **当前普通话：V19片尾雄浑重录接片版（2026-10-27），已完成，待观看。** 用户选择“候选1：三句A参数，品牌名低音高”，本版使用已选同一7.10秒WAV，语速／音高／句间0.60与0.90秒／品牌内0.27秒保持，不再生成或拉伸。只替换89.833333秒后的普通话片尾混音及最后两条字幕时序；98.733333秒时长不变。粤／英仍V15，V16保留为已否定片尾历史。
>
> “山”自然收音约0.37秒，用户在明确披露短于稿内0.6–0.8秒后选择候选1；本次未人工拉伸凑指标。候选获选与整片批准分开，待观看最终接片效果。续做入口qa/v19/film/FINAL_QA.md、IMPLEMENTATION.md、verification.json和qa/v19/COMPLETE_ENDING_SELECTION.json。

'''
links=f"[普通话V19完整版]({r['full']['file']}) · [15秒片尾预览]({r['preview']['file']}) · [粤语V15](out/BOI-HK_史詩形象片_v15_粵語_細節與聲音精修版.mp4) · [英文V15](out/BOI-HK_史詩形象片_v15_英文_細節與聲音精修版.mp4)。\n\n"
p=V/'README.md';s=p.read_text();p.write_text(entry+links+s[s.index('# 美国60秒'):])
p=V.parent/'CLAUDE_HANDOFF.md';s=p.read_text();p.write_text(entry+'新入口video/src/index-v19.tsx、timeline-v19-cn.json、BOI-HK-Epic-v19-CN。片尾原候选SHA不变；先看video/qa/v19/film/FINAL_QA.md，不再回到候选选择或登录／额度审批。\n\n'+s[s.index('> **最新入口：Prompt18美国'):])
p=V/'qa/v11/CURRENT_SELECTION.json';x=json.loads(p.read_text());x['prior_v19_voice_selection_video']=json.loads(json.dumps(x['video_candidate']));x['video_candidate']['locales']['cn']={'path':'video/'+r['full']['file'],'seconds':r['full']['seconds'],'frames':r['full']['frames'],'composition':'BOI-HK-Epic-v19-CN','entry':'video/src/index-v19.tsx','qa':'video/qa/v19/film/verification.json'};x['video_candidate']['preview']='video/'+r['preview']['file'];x.update(updated='2026-10-27',phase='hk_v19_candidate1_integrated_pending_film_review',next_gate='User watches V19 full movie/15s preview. No pending voice selection.',voice_status='Complete Prompt19 candidate1 selected by user; native A timing/pitch retained. No WSOLA, post pitch shift, Happy or crescendo.');x['v19']={'selection':'video/qa/v19/COMPLETE_ENDING_SELECTION.json','bodyPCMUnchangedUntilSeconds':89.83333333333333,'review':'Complete voice selected; movie review pending'};p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
(Q/'IMPLEMENTATION.md').write_text('''# V19 已选候选1接片

2026-10-27，用户选择候选1：三句A参数，品牌名低音高。第一句A试听门及完整候选选择门均已通过，无需再问。整片效果仍待本次观看，不把候选选择等同公司定稿。

同一 ending-candidate-1.wav / SHA58c75b7703066971e27afec15329f84cdb3712053ecb40ed5ac77cd925b7bc10，7.10秒。没有改语速、音高、字音、尾音长度或相对表演；原候选包含固定EQ／仅尾端4%房间余韵。句间0.60／0.90秒，宏泰和国际间0.27秒。山自然收音约0.37秒，已在选择前披露，保留用户选择，不伪称满足0.6–0.8秒。

89.833333秒插入，96.933333秒完整余韵结束，原片98.733333秒结束，容得下且保留最终停留。此前母带4312000样本每声道逐采样保留。原A配乐和淡出仍在，保留原名义音乐母带增益与duck阈值／时间，检测声道按原母带系数反缩放。只有新尾段固定−0.08dB响度校准及峰值保护，无渐强；40ms接点在新声前留白内，尾段实测−16.02LUFS／−1.40dBTP。不全片重新归一化。

只改caption-23／24时序，文字不变；按真实主发声边界前40ms、后150ms取整。语音活动验证用primary dry phonation，房间余韵不是新台词：第二句结束后约一帧房间反射超过−38dBFS不算发声。其余字幕与时间轴不动。

画面组件直接复用V15人物与图片，树生长、中心扩散、去水印等不改。从V16既有I帧2510接入新渲染452帧后缀，前2510帧视频copy。全前段decoded framemd5相等；后缀因字幕重渲不称H264像素完全相同。15秒预览是最后450帧。src/index-v19.tsx及EpicFilmEndingV19.tsx独立入口，旧版都保留。

通用前缀比较工具可独立核验；媒体／参数／客户工程本地保存，只有审阅过的通用工具与同步说明进入Private工具仓。知识库状态与Git阶段结果另见DELIVERY_STATUS.md。
''')
s='# V19 技术核对\n\n'
for kind in ['full','preview']:
 x=r[kind];s+=f"- {kind}：{x['seconds']:.6f}秒／{x['frames']}帧，{x['integratedLUFS']:.2f}LUFS／{x['truePeakDBTP']:.2f}dBTP，完整解码通过；有声1080p30／AAC48k立体声。\n"
s+=f"\n{r['protectedFilesUnchanged']}个保护文件SHA不变；候选1源SHA保持。89.833333秒前母带PCM逐样本一致；前2510画面逐帧解码一致。30条字幕主发声活动全覆盖，无交叠；12帧排版抽样无文字越界。TypeScript通过。尾段混音−16.02LUFS／−1.40dBTP，与全片响度分开，不冒称全片−16LUFS。独立ASR沿用同一候选既有结果“大展宏图 稳如泰山 宏泰国际”。\n\n已查看实际树生长中段及品牌完整落版抽样。影片与预览全解码不代替用户听感；候选1已由用户选定，接片后整体效果待观看。山的自然收音未达原稿长音数值，如实保留。未重新生成语音／增加费用，未发布或上传客户媒体。证据verification.json、audio-implementation.json、audio-prefix-parity.json、video-prefix-parity.json及layout-audit.json。\n"
(Q/'FINAL_QA.md').write_text(s)
print('V19 delivery docs saved.')
