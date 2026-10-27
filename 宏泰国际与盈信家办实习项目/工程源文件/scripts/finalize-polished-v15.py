from pathlib import Path
import json,hashlib,shutil
V=Path(__file__).resolve().parents[1];R=V.parent;Q=V/'qa/v15';r=json.loads((Q/'verification.json').read_text());p=json.loads((Q/'preflight.json').read_text());visual=json.loads((Q/'visual-check.json').read_text());assert len(r['results'])==3
for v in r['results'].values():assert hashlib.sha256((V/v['file']).read_bytes()).hexdigest()==v['sha256']
preview=json.loads((Q/'preview.json').read_text());assert (V/preview['file']).exists()
entry='''> **当前香港版本：V15细节与声音精修版（2026-10-27），三语已完成，待用户观看。** 扩散从画布正中心完整展开；全片去左下小水印；郑健丽贴相框底边，胡忠瑶在同规格卡片内缩小25%；人声总线+1.5dB／A曲总线−1.5dB，普通话片尾用原批准男声重新生成，字幕随新停顿修正。
>
> 粤语102.566667秒／英文98.933333秒／普通话98.733333秒，保持V14各语言时长和正文节奏。当前入口src/index-v15.tsx、timeline-v15-{yue,en,cn}.json、BOI-HK-Epic-v15*。原V14及美国系列独立保留；新版技术通过不等于用户听感或公司发布批准。

'''
links='[粤语完整版](out/BOI-HK_史詩形象片_v15_粵語_細節與聲音精修版.mp4) · [英文完整版](out/BOI-HK_史詩形象片_v15_英文_細節與聲音精修版.mp4) · [普通话完整版](out/BOI-HK_史詩形象片_v15_簡中_細節與聲音精修版.mp4) · [修订重点预览]('+preview['file']+') · [技术核对](qa/v15/FINAL_QA.md)。\n\n'
backup=Q/'before-delivery-docs';backup.mkdir(exist_ok=True)
for rel in ['README.md','../CLAUDE_HANDOFF.md','qa/v11/CURRENT_SELECTION.json','qa/v13/people/PREPARATION_STATUS.md']:
 src=V/rel;dst=backup/rel.replace('../','root/');dst.parent.mkdir(parents=True,exist_ok=True)
 if not dst.exists():shutil.copy2(src,dst)
f=V/'README.md';s=f.read_text();f.write_text(entry+links+s[s.index('# 美国60秒'):])
f=R/'CLAUDE_HANDOFF.md';s=f.read_text();f.write_text(entry+'当前只读video/qa/v15/FINAL_QA.md、IMPLEMENTATION.md、VOICE_PROVENANCE.md和verification.json。重现node scripts/render-polished-v15.mjs（拒绝覆盖）。V14英文审校沿用，当前不再有待生成配音；普通话仅片尾换录。\n\n'+s[s.index('> **最新入口：Prompt18美国'):])
f=V/'qa/v11/CURRENT_SELECTION.json';x=json.loads(f.read_text());x['prior_v14_candidate']=x['video_candidate'];x.update({'updated':'2026-10-27','phase':'hk_v15_polished_complete_pending_user_review','evidence':'user_requested_revision; technical_validation_complete; subjective_film_approval_pending','next_gate':'User watches V15 full three-language films, especially re-recorded Mandarin ending.','voice_status':'V15: same approved clone, CN final two cues re-recorded with pauses, all three mixes VO +1.5dB / A BGM -1.5dB before final mastering.','video_candidate':{'path':'video/'+r['results']['yue']['file'],'entry':'video/src/index-v15.tsx','composition':'BOI-HK-Epic-v15','status':'completed_internal_review_not_user_approved','qa':'video/qa/v15/verification.json','sha256':r['results']['yue']['sha256'],'locales':{k:{'path':'video/'+v['file'],'seconds':v['seconds'],'frames':v['frames']} for k,v in r['results'].items()},'preview':'video/'+preview['file']},'v15':{'scope':'centered full iris, no watermark, portrait framing, mix balance, Mandarin ending','protectedUnchanged':r['protectedFilesUnchanged']}});f.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
(V/'qa/v13/people/PREPARATION_STATUS.md').write_text('# 当前制作已完成：V15精修版\n\n2026-10-27。当前入口video/qa/v15/FINAL_QA.md、README和CURRENT_SELECTION。人物／转场／混音及普通话片尾修正已经交付，无待登录／额度／配音阻塞。旧V14是历史，保持不覆写。下一步用户观看三语新片。\n')
s='# V15 最终技术核对\n\n2026-10-27。根据用户最新六项直接反馈。当前待用户观看与听感反馈，未对外发布。\n\n'
for loc,v in r['results'].items():s+=f"- {loc}：[完整视频](../../{v['file']})；{v['seconds']:.6f}秒／{v['frames']}帧；{v['bytes']}字节；{v['integratedLUFS']:.2f}LUFS／{v['truePeakDBTP']:.2f}dBTP；SHA256 {v['sha256']}。\n"
s+='''
三片均1920×1080／30fps／H264／AAC48k立体声，完整解码通过；AAC与各自PCM母带相关系数均>0.999，无数字削波。容器AAC尾垫和视频时长分开记录，不声称逐包一致。重点预览已完整解码，按转场、郑健丽、五人墙、普通话片尾顺序选段。

## 已完成

- 扩散圆心960,540。当前原生帧从零进度展开，三语+1／+3帧的米白连通区域中心误差≤1.5px，至+6帧面积连续增加；较大圆与原米白Logo接触后不再用连通区域包围盒测圆心。旧缩短句间导致跳过动画起步的问题也已补齐，切点和各片总时长不变。
- 全部V15不显示左下审片小水印与其合并小字。主口号和底部旁白字幕保持。
- 郑健丽原图不拉伸，按实际alpha底边锚定卡片底部；抽样最大底边差0.012px。胡忠瑶图像等比缩至旧75%，卡片仍300×400，实际原图倍率约1.163；所有人物保持弱彩和1.6上限。
- 人声源总线+1.5dB、A音乐源总线−1.5dB，经duck与两遍母带目标−13.8LUFS。增益以外粤／英全语音、普通话片尾前语音与V14逐采样误差<1.2e−7；未变速／裁口播。B/C备份未载入。
- 普通话片尾同已批准克隆重新生成，速度0.94、三处停顿，完整6.28725秒源保留。独立ASR正确识别字词；实际−40dBFS静区约0.83／1.12／0.59秒（标点停顿+标签综合结果），没有把标签数值冒充实测停顿。最后两条字幕按新波形调整。

## 边界与证据

'''
s+=f"{r['nativeFrameRecords']}份原生抽样记录0文字越界；三语90句−38dBFS以上语音活动均在字幕窗内，窗口不重叠。起止覆盖不等于人工逐音素听审。原{r['protectedFilesUnchanged']}个保护文件SHA保持，含V14与美国源／成片。TypeScript通过。\n\n"
s+='英文沿用V14已审校的自然美式稿与完整声音，本次未改译文或换声；参看../v14/ENGLISH_REVIEW.md。音调自然度、宏伟感及公司接受程度仍由用户观看判断。\n\n证据：verification.json、preflight.json、visual-check.json、audio-boundary-check.json、VOICE_PROVENANCE.md、cn-ending-alignment.json、actual-storyboard.jpg及三语SRT。\n'
(Q/'FINAL_QA.md').write_text(s)
print('V15 delivery docs saved')
